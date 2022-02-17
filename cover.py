"""
Cover Platform Device for Wiser.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from functools import partial

import voluptuous as vol



from homeassistant.components.cover import (
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    STATE_CLOSED,
    STATE_OPEN,
    STATE_CLOSING,
    STATE_OPENING,
    ATTR_CURRENT_POSITION,
    ATTR_POSITION,
    CoverEntity
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt

from wiserHeatAPIv2.wiserhub import (
    TEMP_MINIMUM,
    TEMP_MAXIMUM
)

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    WISER_SERVICES
)
from .helpers import get_device_name, get_identifier, get_room_name, get_unique_id

import logging


MANUFACTURER='Schneider Electric'

_LOGGER = logging.getLogger(__name__)

ATTR_COPYTO_ENTITY_ID = "to_entity_id"
ATTR_FILENAME = "filename"
ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

STATUS_AWAY = "Away Mode"
STATUS_AWAY_BOOST = "Away Boost"


WISER_PRESET_TO_HASS = {
    "FromAwayMode": STATUS_AWAY,
    "FromManualMode": None,
    "FromSchedule": None,
}

"""
WISER_PRESETS = {
    "Advance Schedule": 0,
    "Cancel Overrides": 0
}
WISER_PRESETS.update(WISER_BOOST_PRESETS)
"""
"""
SHUTTER_MODE_WISER_TO_HASS = {
        "Auto": shutter_MODE_AUTO,
        "Manual": shutter_MODE_HEAT,
        "Off": shutter_MODE_OFF,
}
"""
"""
SHUTTER_MODE_HASS_TO_WISER = {
    shutter_MODE_AUTO: "Auto",
    shutter_MODE_HEAT: "Manual",
    shutter_MODE_OFF: "Off",
}
"""

SUPPORT_FLAGS =  SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP
#| STATE_CLOSED | STATE_OPEN | STATE_CLOSING | STATE_OPENING,




async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser shutter device."""

    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    wiser_shutters = []
    if data.wiserhub.devices.shutters:
        _LOGGER.debug("Setting up shutter entities")
        for shutter in data.wiserhub.devices.shutters.all :
            if shutter.product_type=="Shutter":
                wiser_shutters.append ( 
                    WiserShutter(data, shutter.id ) 
                )
        async_add_entities(wiser_shutters, True)       

    # Setup services
    platform = entity_platform.async_get_current_platform()



    platform.async_register_entity_service(
        WISER_SERVICES["SERVICE_GET_SHUTTER_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_get_schedule"
        )

    platform.async_register_entity_service(
        WISER_SERVICES["SERVICE_SET_SHUTTER_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_set_schedule"
        )

    platform.async_register_entity_service(
        WISER_SERVICES["SERVICE_COPY_SHUTTER_SCHEDULE"],
            {
                vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
            },
            "async_copy_schedule"
        )


class WiserShutter(CoverEntity):
    """Wisershutter ClientEntity Object."""

    def __init__(self, data, shutter_id):
        """Initialize the sensor."""
        self._data = data
        self._shutter_id = shutter_id
        self._shutter = self._data.wiserhub.devices.shutters.get_by_id(self._shutter_id)
        self._name = self._shutter.name
        
#        self.current_position = None
#        self.position = self._shutter.scheduled_lift
#        self._shutter_modes_list = [modes for modes in shutter_MODE_HASS_TO_WISER.keys()]

        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._shutter.name} requested hub update")
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async update method."""
        self._shutter = self._data.wiserhub.devices.shutters.get_by_id(self._shutter_id)
      
    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_FLAGS
    
    @property
    def current_cover_position(self):
        """Return current position from data."""
        return self._shutter.current_lift

    @property
    def scheduled_position(self):
        """Return scheduled position from data."""
        return self._shutter.scheduled_lift


    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._shutter_id,"shutter"),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._shutter_id,"shutter"))},
                "manufacturer": MANUFACTURER,
                "model": "NHPB/SHUTTER/1",  # get_device_name(self._data, self._shutter_id,"shutter"),`
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon to show if shutter is closed or Open."""
        
        return "mdi:window_shutter" if self.is_closed else "mdi:window_shutter_open"
        

    @property
    def shutter_modes(self):
        """Return the list of available operation modes."""
        return self._shutter_modes_list


    @property
    def name(self):
     #   Return Name of device.
        return f"{get_device_name(self._data, self._shutter_id)}"   
        """ {self._name}"""


    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return True

    @property
    def is_open(self):
        return True if self._shutter.is_open else 'OFF'
        
    @property
    def is_closed(self):
        return True if self._shutter.is_closed else 'OFF'  

    @property
    def current_state(self):
        if self._shutter.is_open :
            return "Open"
        elif  self._shutter.is_closed :
            return "Closed"
        elif (self._shutter.is_open == False and self._shutter.is_closed == False):
            return "Middle"
        #return True if self._shutter.is_open else 'OFF'
         
    @property
    def shutter_unit(self):
        """Return percent units."""
        return "%"

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-Wisershutter-{self._shutter_id}-{self.name}"
        
   
    @property
    def target_scheduled_lift(self):
        """Return target lift."""
        return self._shutter.target_scheduled_lift

    @property
    def lift_open_time(self):
        """Return target lift."""
        return self._shutter.drive_config.get("LiftOpenTime")
         

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes
        attrs["name"] = self._shutter.name
        attrs["shutter_id"] = self._shutter_id

        attrs["mode"] = self._shutter.mode
       
        attrs["control_source"] = self._shutter.control_source
        attrs["is_open"] = self._shutter.is_open
        attrs["is_closed"] = self._shutter.is_closed
        if self._shutter.is_open :
            attrs["current_state"] = "Open"
        elif  self._shutter.is_closed :
            attrs["current_state"] ="Closed"
        elif (self._shutter.is_open == False and self._shutter.is_closed == False):
            attrs["current_state"] = "Middle" 
        attrs["current_lift"] = self._shutter.current_lift
        attrs["manual_lift"] = self._shutter.manual_lift
        attrs["target_lift"] = self._shutter.target_lift
        attrs["scheduled_lift"] = self._shutter.scheduled_lift
        attrs["lift_movement"] = self._shutter.lift_movement
        attrs["is_open"] = self._shutter.is_open
        attrs["is_closed"] = self._shutter.is_closed
        attrs["lift_open_time"] = self._shutter.drive_config.open_time
        attrs["lift_close_time"] = self._shutter.drive_config.close_time
        attrs["schedule_id"] = self._shutter.schedule_id
        
        if  self._data.wiserhub.rooms.get_by_id(self._shutter.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(self._shutter.room_id).name
        else:
            attrs["room"] = "Unassigned"     
        
        if self._shutter.schedule:
            attrs["next_schedule_change"] = str(self._shutter.schedule.next.time)
            attrs["next_schedule_state"] = self._shutter.schedule.next.setting    
            
            
        return attrs

    async def async_set_cover_position(self, **kwargs):
        """Set new target position."""
        position = kwargs.get(ATTR_POSITION)
       
        if position is  not None:
#            return False

#            await self.hass.async_add_executor_job(
#                self._shutter.set_cover_position, position, self._data._position
#            )
          pass    
        else:
#            _LOGGER.debug(f"Setting percentage for {self.name} to {target_percentage}")
#            await self.hass.async_add_executor_job(
#                self._shutter.set_cover_position,position, self._data._position
#            )
          pass
        await self.async_force_update()
        return True

    async def async_open_cover(self, **kwargs):
        """Turn light on."""
        if ATTR_POSITION in kwargs:
            position = int(kwargs[ATTR_POSITION])
        else:
            position = self.current_cover_position
        if position is not None:
            # Below functions need adding to api first
            """
            await self.hass.async_add_executor_job(
                setattr, self._shutter, "current_cover_position", current_cover_position
            )
            """
            pass
        else:
            """
            await self.hass.async_add_executor_job(
                self._shutter.open_cover
            )
            """
            pass
        await self.async_force_update()
        return True

    async def async_close_cover(self, **kwargs):
        """Close shutter"""
        # Below function needs adding to api first
        """
        await self.hass.async_add_executor_job(
            self._shutter.close_cover
        )
        """
        await self.async_force_update()
        return True


    @callback
    async def async_get_schedule(self, filename: str) -> None:
        try:
            if self._shutter.schedule:
                _LOGGER.info(f"Saving {self._shutter.name} schedule to file {filename}")
                await self.hass.async_add_executor_job(
                    self._shutter.schedule.save_schedule_to_yaml_file, filename
                    )
            else:
                _LOGGER.warning(f"{self._shutter.name} has no schedule to save")	
        except:
            _LOGGER.error(f"Saving {self._shutter.name} schedule to file {filename}")

    @callback
    async def async_set_schedule(self, filename: str) -> None:
        try:
            if self._shutter.schedule:
                _LOGGER.info(f"Setting {self._shutter.name} schedule from file {filename}")
                await self.hass.async_add_executor_job(
                    self._shutter.schedule.set_schedule_from_yaml_file, filename
                    )
                await self.async_force_update()
            else:
                _LOGGER.warning(f"{self._shutter.name} has no schedule to assign")
				
        except:
            _LOGGER.error(f"Error setting {self._shutter.name} schedule from file {filename}")

    @callback
    async def async_copy_schedule(self, to_entity_id)-> None:
        to_shutter_name = to_entity_id.replace("shutter.wiser_","").replace("_"," ")
        try:
            if self._shutter.schedule:
                # Add Check that to_entity is of same type as from_entity
                _LOGGER.info(f"Copying schedule from {self._shutter.name} to {to_shutter_name.title()}")
                await self.hass.async_add_executor_job(
                    self._shutter.schedule.copy_schedule, self._data.wiserhub.shutters.get_by_name(to_room_name).schedule.id
                    )
                await self.async_force_update()
            else:
                _LOGGER.warning(f"{self._shutter.name} has no schedule to copy")	
        except:
            _LOGGER.error(f"Error copying schedule from {self._shutter.name} to {to_shutter_name}")


    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""
        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )