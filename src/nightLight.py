import json
import math
import os
from datetime import datetime, timedelta
import threading
import logging

import pytz

from lifxlan import LifxLAN, Light
import ShellyPy
from sunset_calculator import sunsetCalculator

from flask import Flask, request

app = Flask(__name__)
MAINTHREAD = None
RUNNING = False

DEFAULT_CONFIG_FILEPATH = os.path.join("../configs","default.json")
DEFAULT_LOG_FILEPATH = os.path.join(os.getcwd(), "../logs")

# Bulb/light colour example 
# color is [Hue, Saturation, Brightness, Kelvin]
# all values are uint16, max value 65535
WARM_WHITE = [58275, 0, 65535, 3200] # TODO why is the hue not max value?

NEXTSUNSET = None

class NightLightEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__   

class NightLightConfig():
    def __init__(self,lights,plugs,latitude,longitude,sunsetOffset,lightHue,lightSaturation,lightBrightness,lightTemperature,transitionDuration):
        # list of connected lights
        self.lights = lights

        # list of switches
        self.plugs = plugs

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

def loadConfig():
    if not os.path.exists(DEFAULT_CONFIG_FILEPATH):
        print("No config file found.")
        return None
    with open(DEFAULT_CONFIG_FILEPATH) as inFile:
        return NightLightConfig.loadFromJson(json.load(inFile))
       

def getUserConfig():
    lightCount = getSettingInput("Number of lights",0)
    plugCount =  getSettingInput("Number of plugs",0)
    lifx = LifxLAN(lightCount)       
    latitude = getSettingInput("Latitude", -90, 90)
    longitude = getSettingInput("Longitude", -180, 180)
    sunsetOffset = getSettingInput("Sunset Offset (mins)", 0, 720) # 720 mins = 12 hours
    lightBrightness = getSettingInput("Max Brightness Setting", 0, 1)
    lightTemperature = getSettingInput("Light Temperature (Kelvin)", 2500, 9000)
    transitionDuration = getSettingInput("Transition Duration (sec)", 0,3600) # 3600 secs = 1 hour
                
    return NightLightConfig(lifx.get_lights(),latitude,longitude,sunsetOffset,lightBrightness,lightTemperature,transitionDuration)

def Shutdown():
    exit()

def Run():
    config = loadConfig()
    if(config == None):
        return "No configuration found, unable to run night-light."
    while(True):
        NEXTSUNSET = sunsetCalculator.getNextSunset(config.latitude,config.longitude)
        lightTransitionStartTime = NEXTSUNSET -  timedelta(seconds=config.transitionDuration)
        while(True or RUNNING): # TODO is it better to poll or sleep?
            currentTime = datetime.now(pytz.UTC)
            if(lightTransitionStartTime < currentTime):
                break
        color = [config.lightHue,config.lightSaturation,config.lightBrightness,config.lightTemperature]
        for light in config.lights: 
            light.set_color(color,config.transitionDuration)
            light.set_power("on")
        for switch in config.switches:
            switch.relay(0, turn=True)

@app.route("/stop")
def stop():
    RUNNING = False
    if not MAINTHREAD.is_alive():
        return True
    else:
        return False

@app.route("/stop")
def start():
    MAINTHREAD.start()
    if  MAINTHREAD.is_alive():
        RUNNING = True
        return True
    else:
        return False


@app.route("/restart")
def restart():
    res = stop()
    if not res:
        return "Failed to stop night-light."
    res = start()
    if not res:
        return "Failed to start night-light."
    return "night-light restarted successfully."


def startup():
    print(DEFAULT_LOG_FILEPATH)
    if not  os.path.exists(DEFAULT_LOG_FILEPATH):
        os.mkdir(DEFAULT_LOG_FILEPATH)
    log_file = os.path.join(DEFAULT_LOG_FILEPATH,"night-light.log")
    print(log_file)
    open(log_file, 'a').close()
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    return

@app.route("/update-settings")
def updateConfig():
    setting = request.args.get('setting')
    value = request.args.get("value")
    CONFIG[setting] = value

@app.route("/getNextSunset")
def getNextSunset():
    test = sunsetCalculator.getNextSunset(50.0,0.0)
    print(type(test))
    return sunsetCalculator.getNextSunset(50,0).strftime(" %H:%M:%S, %d/%m/%Y")
    #return NEXTSUNSET #TODO: Maybe some nice ascii art with a timeline



if __name__ == '__main__':
    MAINTHREAD = threading.Thread(target=Run)
    startup()
    MAINTHREAD.start()
    app.run(host="0.0.0.0")
