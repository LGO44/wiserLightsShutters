#wiserLightsShutters
  Developpment of lights and shutters for the wiserHomeAssistantPlatform

Developped by LGO44
based on  the wiserHomeAssistantPlatform
climate.py for light.py and cover.py to be able to use the services about the schedule

##new features
For the heatingactuators, I have alos added two sensors for the energy management in the sensor.py


For light and shutters I can use all the attributes provided by the wiserHeatAPIv2.
Some attributes are not provided by this API:
 in the file light.py from the wiserHeatAPIv2 I propose to add the properties: 
 
@property
def manual_level(self):
    """Get the manual level of WiserLight"""
    return self._device_type_data.get("ManualLevel", 0)
    
@property
def override_level(self) -> int:
    """Get the light override level"""
    return self._device_type_data.get("OverrideLevel", 0) 
		

### Issue
When I try to save the schedule of a light or a shutter the result is always:
for example, lustre_cuisine.yaml

null
...
 
 The json schedule file shows 3 types of schedules : 
	"Heaating"		rooms
	"On_off"		smartplugs
	"Level"        	for ligths and shutters    

#### not implemented
The commands for lights and shutters are not operationnal.
	