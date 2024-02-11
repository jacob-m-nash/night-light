from lifxlan import Light
from pathlib import Path
import json
import ShellyPy

WARM_WHITE = [58275, 0, 65535, 3200]
class NightLightConfig():
    def __init__(self,lights: list = [],switches: list = [],latitude: float = 51.5072,longitude: float = 0.1276,sunsetOffset: int = 10,lightHue: int = 58275,lightSaturation: int = 0,lightBrightness: int = 65535,lightTemperature: int = 3200,transitionDuration: int = 120) -> None:
        # list of connected lights
        self.lights = lights
        self.switches = switches

        # sunset settings
        self.latitude = latitude
        self.longitude = longitude
        self.sunsetOffset = sunsetOffset
        
        # light/bulb settings
        self.lightHue = lightHue
        self.lightSaturation = lightSaturation
        self.lightBrightness = lightBrightness
        self.lightTemperature = lightTemperature
        self.transitionDuration = transitionDuration 


    def save(self,filepath:Path):
         try:
              filepath.parent.mkdir(parents=True, exist_ok=True)
              with open(filepath, 'w') as f:
                   json.dump(self,f, indent=4, sort_keys=True,cls=NightLightConfigEncoder)
         except Exception as e:
              raise Exception(f"Failed to save Night Light config at {filepath}") from e
         return

    @staticmethod
    def load(filepath:Path):
        with open(filepath) as configFile:
            return NightLightConfig.loadFromJson(json.load(configFile))

    @staticmethod
    def loadFromJson(jsonDict):
        lights = []
        switches = []
        for light in jsonDict["lights"]:
            lights.append(Light(light["mac_addr"],light["ip_addr"],light["service"],light["port"],light["source_id"],light["verbose"]))
        for switchAddress in jsonDict["switches"]:
             switches.append(ShellyPy.Shelly(switchAddress))

        return NightLightConfig(lights,switches,jsonDict["latitude"],jsonDict["longitude"],jsonDict["sunsetOffset"],jsonDict["lightHue"],jsonDict["lightSaturation"],jsonDict["lightBrightness"],jsonDict["lightTemperature"],jsonDict["transitionDuration"])

class NightLightConfigEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__