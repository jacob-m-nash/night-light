import numpy as np
from sunset_calculator import sunsetCalculator
from lifxlan import LifxLAN
import math
import os
import json
from json import JSONEncoder
from datetime import datetime,timezone, timedelta

class MyEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__   

class NightLightConfig():
    def __init__(self,lights,latitude,longitude,sunsetOffset,maxLightBrightness,lightTemperature,transitionDuration):
        self.lights = lights
        self.latitude = latitude
        self.longitude = longitude
        self.sunsetOffset = sunsetOffset
        self.maxLightBrightness = maxLightBrightness
        self.lightTemperature = lightTemperature
        self.transitionDuration = transitionDuration * 1000


    @staticmethod
    def loadFromJson(jsonDict):
        return NightLightConfig(jsonDict["lights"],jsonDict["latitude"],jsonDict["longitude"],jsonDict["sunsetOffset"],jsonDict["maxLightBrightness"],jsonDict["lightTemperature"],jsonDict["transitionDuration"])


def loadConfig():
    configFileName = "configs/config.json"
    if not os.path.exists(configFileName):
        print("No config file found.")
        return None
    with open(configFileName) as inFile:
        return NightLightConfig.loadFromJson(json.load(inFile))


def saveConfig(config):
    with open("configs/config.json", "w") as outfile: # TODO remove yucky hard coded file path
        outfile.write(MyEncoder().encode(config))


def getSettingInput(settingName,minValue = -math.inf,maxValue = math.inf):
    while(True):
        settingValue = float(input(f"{settingName}: "))
        if( minValue <= settingValue <= maxValue ):
            return settingValue
        else:
            print(f"Invalid {settingName}, value must be in range {minValue} - {maxValue}")


def getUserConfig():
    lightCount = getSettingInput("Number of lights",0) 
    lifx = LifxLAN(lightCount)       
    latitude = getSettingInput("Latitude", -90, 90)
    longitude = getSettingInput("Longitude", -180, 180)
    sunsetOffset = getSettingInput("Sunset Offset (mins)", 0, 720) # 720 mins = 12 hours
    maxLightBrightness = getSettingInput("Max Brightness Setting", 0, 1)
    lightTemperature = getSettingInput("Light Temperature (Kelvin)", 2500, 9000)
    transitionDuration = getSettingInput("Transition Duration (sec)", 0,3600) # 3600 secs = 1 hour
                
    return NightLightConfig(lifx.get_lights(),latitude,longitude,sunsetOffset,maxLightBrightness,lightTemperature,transitionDuration)

def Run():
    config = loadConfig()
    if(config == None):
        config = getUserConfig()
        saveConfig(config)
    while(True):
        nextSunset = sunsetCalculator.getNextSunset(config.latitude,config.longitude)
        lightTransitionStartTime = nextSunset -  timedelta(seconds=config.transitionDuration)
        currentTime = datetime.now(timezone.utc)
        while(True): # TODO is it better to poll or sleep?
            if(lightTransitionStartTime < currentTime): # FIXME TypeError: can't compare offset-naive and offset-aware datetimes
                break
        # color is [Hue, Saturation, Brightness, Kelvin]
        # all values are uint16, max value 65535
        WARM_WHITE = [58275, 0, 65535 * config.maxLightBrightness, config.lightTemperature] # TODO why is the hue not max value?
        color = WARM_WHITE
        for light in config.lights:
            light.setColor(color,config.transitionDuration)

if __name__ == '__main__':
    # lightController.lightController.FindLights()
    print("Running...")
    Run()
