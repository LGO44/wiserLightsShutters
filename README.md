# wiserLightsShutters
  Developpment of lights and shutters for the wiserHomeAssistantPlatform

Developped by LGO44
based on 
climate.py for light.py and cover.py 


## v3.0 New Features

- heatingactuators: 
    I have alos added to sensor for the energy management in the sensor.py

- lights and shutters:
	For light and shutters I can use all the attributes provided by the wiserHeatAPIv2.

Some attributes are not provided by this API:
 
### in the file light.py from the wiserHeatAPIv2 I propose to add the properties: 

@property
def schedule_id(self):
"""Get the schedule id of the light"""
return self._device_type_data.get("ScheduleId", 0) 
 
@property
def manual_level(self):
    """Get the manual level of WiserLight"""
    return self._device_type_data.get("ManualLevel", 0)
    
@property
def output_range_minimum(self):
    """Get the minimum range for the level of WiserLight"""
    return self._device_type_data.get("OutputRange", {'Minimum': 0}).get("Minimum")
    
@property
def output_range_maximum(self):
    """Get the maximum range for the level WiserLight"""
    return self._device_type_data.get("OutputRange", {'Maximum': 0}).get("Maximum")
    
@property
def target_state(self) -> str:
    """Get the light target state On Off"""
    return self._device_type_data.get("TargetState", 0)
    
@property
def target_percentage(self) -> int:
    """Get the light target percentage"""
    return self._device_type_data.get("TargetPercentage", 0)
    
@property
def scheduled_percentage(self) -> int:
    """Get the light scheduled percentage"""
    return self._device_type_data.get("ScheduledPercentage", 0)
    
@property
def override_level(self) -> int:
    """Get the light override level"""
    return self._device_type_data.get("OverrideLevel", 0) 
	
	
###  For the shutters in the shutter.py I propose:

@property
def schedule_id(self):
    """Get the schedule id of the light"""
    return self._device_type_data.get("ScheduleId", 0)

@property
def target_lift(self) -> int:
    """Get the light target lift"""
    return self._device_type_data.get("TargetLift", 0)	
	
