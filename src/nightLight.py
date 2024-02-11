import json
import math
import os
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
import logging
from pathlib import Path
from nightLightAppConfig import NightLightAppConfig
from nightLightConfig import NightLightConfig

import click

import pytz

from lifxlan import LifxLAN
import ShellyPy
from sunset_calculator import sunsetCalculator
from nightLightConfig import NightLightConfig

from flask import Flask, request, jsonify

class RemoveColorFilter(logging.Filter):
    def filter(self, record):
        if record and record.msg and isinstance(record.msg, str):
            record.msg = click.unstyle(record.msg) 
        return True

def run():
    global CONFIG
    if(CONFIG == None):
        return "No configuration found, unable to run night-light."
    while(True):
        NEXT_SUNSET = sunsetCalculator.getNextSunset(CONFIG.latitude,CONFIG.longitude)
        lightTransitionStartTime = NEXT_SUNSET -  timedelta(seconds=CONFIG.transitionDuration)
        while(True or RUNNING): # TODO is it better to poll or sleep?
            currentTime = datetime.now(pytz.UTC)
            if(lightTransitionStartTime < currentTime):
                break
            sleep(1)
        color = [CONFIG.lightHue,CONFIG.lightSaturation,CONFIG.lightBrightness,CONFIG.lightTemperature]
        for light in CONFIG.lights: 
            light.set_color(color,CONFIG.transitionDuration)
            light.set_power("on")
        for plug in CONFIG.plugs:
            plug.relay(0, turn=True)


app = Flask(__name__)
APP_CONFIG_PATH = Path(os.getcwd()) / "configs" /  "defaultAppConfig.json"
CONFIG: NightLightConfig = None
MAIN_THREAD = Thread(target=run)

RUNNING = True
NEXT_SUNSET = None


def shutdown():
    exit()

@app.route("/turnOff")
def turnOff():
    for light in CONFIG.lights: 
            light.set_power("off")
    for plug in CONFIG.plugs:
        plug.relay(0, turn=False)

@app.route("/stop")
def stop():
    if not MAIN_THREAD.is_alive():
        MAIN_THREAD._stop_event.set() # TODO this may be dangerous to abruptly stop the thread (could make own thread class)
        RUNNING = False
        return True
    else:
        return False

@app.route("/stop")
def start():
    MAIN_THREAD.start()
    if  MAIN_THREAD.is_alive():
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
    loadAppConfigs()
    createLogger()
    loadNightLightConfig()
    return

def loadAppConfigs():
    if not APP_CONFIG_PATH.exists():
            NightLightAppConfig.GenerateDefaultConfig(APP_CONFIG_PATH)
    appConfig = json.loads(APP_CONFIG_PATH.read_bytes())
    for key in appConfig:
        app.config[key] = appConfig[key]


def createLogger():
    logFile = Path(os.getcwd()) / app.config["nightLightLogs"]
    if not logFile.exists():
        os.mkdir(logFile.parent)
        open(logFile, 'a').close()
    logging.basicConfig(filename=logFile, level=logging.ERROR)
    remove_color_filter = RemoveColorFilter()
    logging.getLogger("werkzeug").addFilter(remove_color_filter)
    return

def loadNightLightConfig():
    global CONFIG
    configPath = Path(os.getcwd())/ app.config["nightLightConfig"]
    # if path
    if not configPath.exists():
        print("no nightlight config found creating default one ") # TODO make log
        CONFIG = NightLightConfig()
        CONFIG.save(configPath)
        return
    CONFIG = NightLightConfig.load(configPath)
    

@app.route("/update-settings")
def updateConfig():
    setting = request.args.get('setting')
    value = request.args.get("value")
    CONFIG[setting] = value

@app.route("/getNextSunset")
def getNextSunset():
    test = sunsetCalculator.getNextSunset(CONFIG.latitude,longitude=CONFIG.longitude) #TODO Remove tests once default config has been created and server can run
    return jsonify(sunsetCalculator.getNextSunset(50,0).strftime("%H:%M:%S"))
    #return NEXTSUNSET #TODO: Maybe some nice ascii art with a timeline



if __name__ == '__main__':    
    startup()
    MAIN_THREAD.start()
    app.run(host="0.0.0.0")

# Notes

