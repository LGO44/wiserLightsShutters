"""
Lights Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from functools import partial

import voluptuous as vol



from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    SUPPORT_BRIGHTNESS_PCT,
    ATTR_BRIGHTNESS_PCT,
    ATTR_SUPPORTED_COLOR_MODES,
    SUPPORT_TRANSITION,
    COLOR_MODES_BRIGHTNESS,
    brightness_supported,
    LightEntity,
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

MAX_BRIGHTNESS = 255
#COLOR_MODES_BRIGHTNESS = "brightness"
MANUFACTURER='Schneider Electric'

_LOGGER = logging.getLogger(__name__)

ATTR_COPYTO_ENTITY_ID = "to_entity_id"
ATTR_FILENAME = "filename"
ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

STATUS_AWAY = "Away Mode"
STATUS_AWAY_BOOST = "Away Boost"

STATUS_AWAY = "Away Mode"
STATUS_OVERRIDE = "Override"

LIGHT_MODE_ON= "Manual"
LIGHT_MODE_AUTO= "Auto"


#WISER_PRESETS.update(WISER_BOOST_PRESETS)


LIGHT_MODE_WISER_TO_HASS = {
        "Auto": LIGHT_MODE_AUTO,
        "Manual": LIGHT_MODE_ON,
        
}


LIGHT_MODE_HASS_TO_WISER = {
    LIGHT_MODE_AUTO: "Auto",
    LIGHT_MODE_ON: "Manual",
}  


SUPPORT_FLAGS = SUPPORT_BRIGHTNESS | SUPPORT_BRIGHTNESS_PCT #| SUPPORT_TRANSITION




async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser light device."""

    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    wiser_lights = []
    if data.wiserhub.devices.lights:
        _LOGGER.debug("Setting up light entities")
        for light in data.wiserhub.devices.lights.all :
            if light.is_dimmable:
                wiser_lights.append (
                WiserLight(data, light.id ) 
               )
        async_add_entities(wiser_lights, True)
       

        # Setup services
        platform = entity_platform.async_get_current_platform()
     
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_GET_LIGHT_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_get_schedule"
            )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_LIGHT_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_set_schedule"
            )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_COPY_LIGHT_SCHEDULE"],
            {
                vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
            },
            "async_copy_schedule"
            )


class WiserLight(LightEntity):
    """WiserLight ClientEntity Object."""

    def __init__(self, data, light_id):
        """Initialize the sensor."""
        self._data = data
        self._light_id = light_id
        self._light = self._data.wiserhub.devices.lights.get_by_id(self._light_id)
        self._name = self._light.name
        self._light_modes_list = [modes for modes in LIGHT_MODE_HASS_TO_WISER.keys()]
        

        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._light.name} requested hub update")
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async update method."""
        self._light = self._data.wiserhub.devices.lights.get_by_id(self._light_id)
      
    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_FLAGS
    
        
    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._light_id,"light"),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._light_id,"light"))},
                "manufacturer": MANUFACTURER,
                "model":  self._light.product_model,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon to show if light is On or off."""
        if self._light.mode == "Auto":
            return "mdi:lightbulb-auto" if self._light.is_on else "mdi:lightbulb-auto-outline"
        else:
            return "mdi:lightbulb" if self._light.is_on else "mdi:lightbulb-outline"

    @property
    def light_modes(self):
        """Return the list of available operation modes."""
        return self._light_modes_list

    @property
    def current_level(self):
        """Return current temp from data."""
        return self._light.current_level

 
    @property
    def output_range_maximum(self):
        """Return max level from data."""
        """ should be self._light.output_range_maximum to be implemented in WiserHeatAPIv2   """
        return self._light.output_range.max

    @property
    def output_range_minimum(self):
        """Return min level from data."""
        """ should be self._light.output_range.minimum to be implemented in WiserHeatAPIv2   """
        return self._light.output_range.min

    @property
    def name(self):
        """Return Name of device."""
        return get_device_name(self._data, self._light_id, "device")


    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return True

    @property
    def mode(self):
        return self._ligth.mode   

    
    @property
    def is_on(self):
        return True if self._light.current_state=="On" else "Off"
      
         
    @property
    def light_unit(self):
        """Return percent units."""
        return "%"

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-WiserLight-{self._light_id}-{self.name}"
        
    @property
    def target_state(self):
        """Return target percentage."""
        return self._light.target_state
   
    @property
    def target_percentage(self):
        """Return target percentage."""
        return self._light.target_percentage
        
    @property
    def scheduled_percentage(self):
        """Return target percentage."""
        return self._light.scheduled_percentage
        
    @property
    def away_action(self):
        """Return target percentage."""
        return self._light.away_action
       
    @property
    def light_mode(self):
        """Return the list of available operation modes."""
        return self._light_mode

    @property
    def light_modes(self):
        """Return the list of available operation modes."""
        return self._light_modes_list
   
    def set_light_mode(self, light_mode):
        """Set new operation mode."""  
        _LOGGER.debug(
            f"Setting LIGHT mode to {light_mode} for {self._light.name}"
        )
        try:
            self._light.mode = LIGHT_MODE_HASS_TO_WISER[light_mode]
            pass
        except KeyError:
            _LOGGER.error(f"Invalid LIGHT mode.  Options are {self.light_modes}")
        self.hass.async_create_task(
            self.async_force_update()
        )
        return True
     

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes
        # Light Identification
        attrs["name"] = self._light.name      
        attrs["model"] = self._light.model
        attrs["product_type"] = self._light.product_type
        attrs["product_identifier"] = self._light.product_identifier
        #attrs["Vendor"] = MANUFACTURER
        attrs["product_model"] = self._light.product_model
        attrs["serial_number"] = self._light.serial_number
        attrs["firmware"] = self._light.firmware_version
        # Room
        if  self._data.wiserhub.rooms.get_by_id(self._light.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(self._light.room_id).name
        else:
            attrs["room"] = "Unassigned" 
        # Settings
        attrs["mode"] = self._light.mode
        attrs["away_mode_action"] = self._light.away_mode_action 
        attrs["is_dimmable"] = self._light.is_dimmable
        attrs["output_range_min"] = self._light.output_range.min
        attrs["output_range_max"] = self._light.output_range.max
        # Command state
        attrs["control_source"] = self._light.control_source
        # Status
        attrs["current_state"] = self._light.current_state
        attrs["current_percentage"] = self._light.current_percentage
        attrs["current_level"] = self._light.current_level
        attrs["target_percentage"] = self._light.target_percentage
        attrs["target_state"] = self._light.target_state
        attrs["manual_level"] = self._light.manual_level
        attrs["override_level"] = self._light.override_level
        # Schedule
        attrs["schedule_id"] = self._light.schedule_id
        if self._light.schedule:
            attrs["next_day_change"] = str(self._light.schedule.next.day)
            attrs["next_schedule_change"] = str(self._light.schedule.next.time)
            attrs["next_schedule_percentage"] = self._light.schedule.next.setting    
        return attrs

    @property
    def brightness(self):
        """Return current brightness from data."""
        return self._light.current_level
        
    async def async_set_light_brightness(self, **kwargs):
        """Set new target level."""
        if ATTR_BRIGHTNESS in kwargs:
            #brightness = int(kwargs.get(ATTR_BRIGHTNESS))
            brightness = int(kwargs[ATTR_BRIGHTNESS])
            _LOGGER.debug(f" Brightness {self.name} = {brightness}")
        else: 
            brightness = self.brightness
       
        if brightness is not None:
           #return False

            _LOGGER.debug(f"Setting percentage for {self.name} to {brightness} ")
            await self.hass.async_add_executor_job(
                self._light.current_percentage, brightness
           )
            pass    
        else:
            _LOGGER.debug(f"Setting percentage for {self.name} to {brightness}")
            await self.hass.async_add_executor_job(
                self._light.turn_on
            )
#          pass
        await self.async_force_update()
        return True


#    async def async_turn_on1(self, **kwargs):
#         """Turn light on."""
        
#        if ATTR_BRIGHTNESS in kwargs:
#            brightness = int(kwargs[ATTR_BRIGHTNESS])
#        else:
#            brightness = self.brightness
#        if brightness is not None:                     
#            # Below functions need adding to api first
#            
#            await self.hass.async_add_executor_job(
#                setattr, self._light, "brightness", brightness
#            )
#            """
#            
#            await self.hass.async_add_executor_job(
#                setattr, self._light, "brightness", brightness
#            )
#            pass
#        else:
#            
#            await self.hass.async_add_executor_job(
#                self._light.turn_on
#            )
#            """
#            await self.hass.async_add_executor_job(
#                self._light.turn_on
#            )
#            pass
#        await self.async_force_update()
#        return True

    async def async_turn_on(self, **kwargs):
        """Turn light off."""
         
        await self.hass.async_add_executor_job(
            self._light.turn_on
        )
        await self.async_force_update()
        return True
    
        
    async def async_turn_off(self, **kwargs):
        """Turn light off."""
 
        await self.hass.async_add_executor_job(
            self._light.turn_off
        )
        await self.async_force_update()
        return True
    


    @callback
    async def async_get_schedule(self, filename: str) -> None:
        try:
            if self._light.schedule:
                _LOGGER.info(f"Saving {self._light.name} schedule to file {filename}")
                await self.hass.async_add_executor_job(
                    self._light.schedule.save_schedule_to_yaml_file, filename
                )
            else:
                _LOGGER.warning(f"{self._light.name} has no schedule to save")
        except:
            _LOGGER.error(f"Saving {self._light.name} schedule to file {filename}")

    @callback
    async def async_set_schedule(self, filename: str) -> None:
        try:
            if self._light.schedule:
                _LOGGER.info(f"Setting {self._light.name} schedule from file {filename}")
                await self.hass.async_add_executor_job(
                    self._light.schedule.set_schedule_from_yaml_file, filename
                )
                await self.async_force_update()
            else:
                _LOGGER.warning(f"{self._light.name} has no schedule to assign")
        except:
            _LOGGER.error(f"Error setting {self._light.name} schedule from file {filename}")

    @callback
    async def async_copy_schedule(self, to_entity_id)-> None:
        to_light_name = to_entity_id.replace("light.wiser_","").replace("_"," ")
        try:
            if self._light.schedule:
                # Add Check that to_entity is of same type as from_entity
                _LOGGER.info(f"Copying schedule from {self._light.name} to {to_light_name.title()}")
                await self.hass.async_add_executor_job(
                    self._light.schedule.copy_schedule, self._data.wiserhub.lights.get_by_name(to_light_name).schedule.id
                )
                await self.async_force_update()
            else:
                _LOGGER.warning(f"{self._light.name} has no schedule to copy")
                
        except:
            _LOGGER.error(f"Error copying schedule from {self._light.name} to {to_light_name}")

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
