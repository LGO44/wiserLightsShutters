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
def manual_level(self):
    """Get the manual level of WiserLight"""
    return self._device_type_data.get("ManualLevel", 0)
    
   
@property
def override_level(self) -> int:
    """Get the light override level"""
    return self._device_type_data.get("OverrideLevel", 0) 
	
### Issue
When I try to save the schedule of a light or a shutter the result is always:
for example from the HA developpment tools, the file lustre_cuisine.yaml 
![image](https://user-images.githubusercontent.com/95585425/154519330-74d6e14c-ff59-4ebd-beb2-0c535baca9e5.png)

null
...
![image](https://user-images.githubusercontent.com/95585425/154519825-93b86fc2-87a6-454a-8118-23ddc11b8abf.png)
 
 The json schedule file shows 3 types of schedules : 
	"Heaating"		rooms
	"On_off"		smartplugs
	"Level"        	for ligths and shutters    

#### not implemented
The commands for lights and shutters are not operationnal.
		

	
