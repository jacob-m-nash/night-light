import json
import os
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from nightLightAppConfig import NightLightAppConfig
from nightLightConfig import NightLightConfig
from lifxlan import LifxLAN

import click

import pytz

import ShellyPy
from sunset_calculator import sunsetCalculator
from nightLightConfig import NightLightConfig

from flask import Flask, request, jsonify, abort

class RemoveColorFilter(logging.Filter):
    def filter(self, record):
        if record and record.msg and isinstance(record.msg, str):
            record.msg = click.unstyle(record.msg) 
        return True

# TODO make to own module
def setupLogging():
    logPath = Path(os.getcwd()) / "logs"
    if not logPath.exists():
        os.mkdir(logPath)

    logger = logging.getLogger('nightLight.app') 
    logger.addFilter(RemoveColorFilter())
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Show info to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    # Log everything but DEBUG to file 
    fileHandler = TimedRotatingFileHandler('logs/app_info.log', when='midnight', interval=1, backupCount=7)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    logger.info("Finished setting up logger.")

    return logger

def run():
    global CONFIG
    if(CONFIG == None):
        logger.error("No configuration found, unable to run night-light.")
        return "No configuration found, unable to run night-light." # TODO what to do here?
    NEXT_SUNSET = sunsetCalculator.getNextSunset(CONFIG.latitude,CONFIG.longitude)
    logger.info(f"Next sunset: {NEXT_SUNSET}") # TODO use custom LoggerAdapter for sunset times  
    while(True):
        lightTransitionStartTime = NEXT_SUNSET -  timedelta(seconds=CONFIG.transitionDuration) - timedelta(minutes=CONFIG.sunsetOffset)
        while(True or RUNNING): # TODO is it better to poll or sleep?
            currentTime = datetime.now(pytz.UTC)
            if(lightTransitionStartTime < currentTime):
                break
            sleep(1)
        color = [CONFIG.lightHue,CONFIG.lightSaturation,CONFIG.lightBrightness,CONFIG.lightTemperature]
        logger.debug("Turning on lights.")
        for light in CONFIG.lights: 
            light.set_color(color,CONFIG.transitionDuration) #TODO remember prev colour/ overwrite colour?
            light.set_power("on")
        logger.debug("Turning on plugs.")
        for plug in CONFIG.plugs:
            plug.relay(0, turn=True)
        NEXT_SUNSET = sunsetCalculator.getNextSunset(CONFIG.latitude,CONFIG.longitude, tomorrow=True)
        logger.info(f"Next sunset: {NEXT_SUNSET}") # TODO use custom LoggerAdapter for sunset times  


app = Flask(__name__)
logger = setupLogging()
APP_CONFIG_FILE = Path(os.getcwd()) / "configs" /  "defaultAppConfig.json" #TODO path combine
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

@app.route("/add")
def add():
    device = request.args.get('device')
    if device == "plug":
        ipAddress = request.args.get('ipAddress')
        try:
            plug = ShellyPy.Shelly(ipAddress)
            CONFIG.plugs.append(plug)
            CONFIG.save(Path(os.getcwd())/ app.config["nightLightConfig"]) #TODO have config have its own file name attribute
            return("Plug {ipAddress} added")
        except Exception as e:
            logger.exception('Failed to add device.')
            return("oh no") #TODO better error handling
    if device == "light":
        lifx = LifxLAN()
        devices = lifx.get_lights()
        for d in devices:
            if d not in CONFIG.lights:
                logger.info("added light")
                CONFIG.lights.append(d)
        CONFIG.save(Path(os.getcwd())/ app.config["nightLightConfig"])
        return(f"New light added {d.label}")

def startup():
    loadAppConfigs()
    loadNightLightConfig()
    return

def loadAppConfigs():
    if not APP_CONFIG_FILE.exists():
            NightLightAppConfig.GenerateDefaultConfig(APP_CONFIG_FILE)
    appConfig = json.loads(APP_CONFIG_FILE.read_bytes())
    for key in appConfig:
        app.config[key] = appConfig[key]


def loadNightLightConfig():
    global CONFIG
    configPath = Path(os.getcwd())/ app.config["nightLightConfig"]
    # if path
    if not configPath.exists():
        logger.warning("No nightlight config found.")
        CONFIG = NightLightConfig()
        logger.info("New nightlight config created.")
        CONFIG.save(configPath)
        logger.info(f"new nightlight config saved at {configPath}.") # TODO use custom LoggerAdapter for filenames 
        return
    CONFIG = NightLightConfig.load(configPath)
    logger.info("Config loaded")
    

@app.route("/update-settings")
def updateConfig():
    setting = request.args.get('setting')
    value = request.args.get("value")
    CONFIG[setting] = value

@app.route("/get")
def get():
    param = request.args.get('param')
    if param == "nextsunset":
        return jsonify(sunsetCalculator.getNextSunset(CONFIG.latitude,CONFIG.longitude).strftime("%H:%M:%S")) #TODO convert to correct timezone 


if __name__ == '__main__':
    logger.info("Running startup.")    
    startup()
    logger.info("startup finished.")
    MAIN_THREAD.start()
    app.run(host="0.0.0.0")

# Notes

