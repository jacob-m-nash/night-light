import numpy as np
from sunset_calculator import sunsetCalculator
from lifxlan.lifxlan import lifxlan

class NightLightConfig:
    def __init__(self,lights,latitude,longitude,sunsetOffset,maxPowerSetting):
        self.lights = lights
        self.latitude = latitude
        self.longitude = longitude
        self.sunsetOffset = sunsetOffset
        self.maxPowerSetting = maxPowerSetting

def loadConfig():
    # TODO load json file of config file

    #If no config return None
    return None

# TODO: what to do if not a range? i.e number of lights only has to be greater than 0
def getSettingInput(settingName,settingRange):
    while(True):
        settingValue = float(input(f"{settingName}: "))
        if(settingValue in settingRange):
            return settingValue
        else:
            print(f"Invalid {settingName}, value must be in range {settingRange}")


def getUserConfig():
    while(True):
        lightCount = int(input("Number of Lights: "))
        if(lightCount > 0):
            lifx = lifxlan.LifxLAN(lightCount)
            break
        else:
            print("Number of lights must be greater than 0. Please try again")
            
    latitude = getSettingInput("Latitude", range(-90,90))
    longitude = getSettingInput("Longitude", range(-180,180))
    maxPowerSetting = getSettingInput("Max power setting", range(0,1))
    sunsetOffset = getSettingInput("Sunset Offset (mins)", range(0,720)) # 720 mins = 12 hours
                
    return NightLightConfig(lifx.get_lights(),latitude,longitude,sunsetOffset,maxPowerSetting)



def Run():
    config = loadConfig()
    if(config == None):
        config = getUserConfig()
    while(True):
        nextSunset = sunsetCalculator.getNextSunset(config.latitude,config.longitude)
        # TODO wait for current time to equal sunset time minus sunsetOffset then...
        for light in config.lights:
            light

        
        
    




if __name__ == '__main__':
    # lightController.lightController.FindLights()
    print("Running...")
    Run()

