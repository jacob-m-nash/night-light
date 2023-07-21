import json
import math
import os
from datetime import datetime, timedelta

import pytz

from lifxlan import LifxLAN, Light
from sunset_calculator import sunsetCalculator

DEFAULT_CONFIG_FILEPATH = os.path.join(os.getcwd(),"configs","defaultConfig.json" )
PIPE_PATH = os.path.join(os.getcwd(),"pipes","pipe") # TODO when setting up write path of pipe to "global" config file 

class NightLightEncoder(json.JSONEncoder):
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
        self.transitionDuration = transitionDuration 


    @staticmethod
    def loadFromJson(jsonDict):
        lights = []
        for light in jsonDict["lights"]:
            lights.append(Light(light["mac_addr"],light["ip_addr"],light["service"],light["port"],light["source_id"],light["verbose"]))

        return NightLightConfig(lights,jsonDict["latitude"],jsonDict["longitude"],jsonDict["sunsetOffset"],jsonDict["maxLightBrightness"],jsonDict["lightTemperature"],jsonDict["transitionDuration"])


def loadConfig():
    if not os.path.exists(DEFAULT_CONFIG_FILEPATH):
        print("No config file found.")
        return None
    with open(DEFAULT_CONFIG_FILEPATH) as inFile:
        return NightLightConfig.loadFromJson(json.load(inFile))


def saveConfig(config):
    with open(DEFAULT_CONFIG_FILEPATH, "w") as outfile:
        outfile.write(NightLightEncoder().encode(config))


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
        currentTime = datetime.now(pytz.UTC)
        while(True): # TODO is it better to poll or sleep?
            if(lightTransitionStartTime < currentTime):
                break
            currentTime = datetime.now(pytz.UTC)
        # color is [Hue, Saturation, Brightness, Kelvin]
        # all values are uint16, max value 65535
        WARM_WHITE = [58275, 0, 65535 * config.maxLightBrightness, config.lightTemperature] # TODO why is the hue not max value?
        color = WARM_WHITE
        for light in config.lights: 
            light.set_color(color,config.transitionDuration,False)
            light.set_power("on")

def waitForCommand():
        with open(PIPE_PATH, 'r') as pipeInput:
            input = pipeInput.readline()
        with open(PIPE_PATH, 'w') as pipeOutput:
            returnStr = "echo: " + input
            pipeOutput.write(returnStr)

def Startup():
    print("Creating pipe")
    if os.path.isfile(PIPE_PATH): # FIXME this does not work, dont know why its not a file or dir
        print(f"Pipe: {PIPE_PATH} already exists using old pipe file.")
        return
    os.mkfifo(PIPE_PATH)
    print(f"Pipe file created at {PIPE_PATH}")

    return


if __name__ == '__main__':
    Startup()
    waitForCommand()
    print("Running...")
    Run()

