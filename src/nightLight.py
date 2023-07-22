import json
import math
import os
from datetime import datetime, timedelta

import pytz

from lifxlan import LifxLAN, Light
from sunset_calculator import sunsetCalculator

DEFAULT_CONFIG_FILEPATH = os.path.join(os.getcwd(),"configs","defaultConfig.json" )
PIPE_PATH = os.path.join(os.getcwd(),"pipes","pipe") # TODO when setting up write path of pipe to "global" config file 

# color is [Hue, Saturation, Brightness, Kelvin]
# all values are uint16, max value 65535
WARM_WHITE = [58275, 0, 65535, 3200] # TODO why is the hue not max value?

class NightLightEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__   

class NightLightConfig():
    def __init__(self,lights,latitude,longitude,sunsetOffset,lightHue,lightSaturation,lightBrightness,lightTemperature,transitionDuration):
        # list of connected lights
        self.lights = lights

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
       

    @staticmethod
    def loadFromJson(jsonDict):
        lights = []
        for light in jsonDict["lights"]:
            lights.append(Light(light["mac_addr"],light["ip_addr"],light["service"],light["port"],light["source_id"],light["verbose"]))

        return NightLightConfig(lights,jsonDict["latitude"],jsonDict["longitude"],jsonDict["sunsetOffset"],jsonDict["lightHue"],jsonDict["lightSaturation"],jsonDict["lightBrightness"],jsonDict["lightTemperature"],jsonDict["transitionDuration"])


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
    lightBrightness = getSettingInput("Max Brightness Setting", 0, 1)
    lightTemperature = getSettingInput("Light Temperature (Kelvin)", 2500, 9000)
    transitionDuration = getSettingInput("Transition Duration (sec)", 0,3600) # 3600 secs = 1 hour
                
    return NightLightConfig(lifx.get_lights(),latitude,longitude,sunsetOffset,lightBrightness,lightTemperature,transitionDuration)

def Shutdown():
    os.remove(PIPE_PATH)
    exit()

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
        color = [config.lightHue,config.lightSaturation,config.lightBrightness,config.lightTemperature]
        for light in config.lights: 
            light.set_color(color,config.transitionDuration)
            light.set_power("on")

def waitForCommand():
    while True:
        with open(PIPE_PATH, 'r') as pipeInput:
            input = pipeInput.readline()
        reply = parseCommand(input)
        if reply is None:
            continue
        with open(PIPE_PATH, 'w') as pipeOutput:
            pipeOutput.write(reply)

def parseCommand(command,args):
    input = str.lower(command)
    if input == "shutdown":
        Shutdown() 

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

