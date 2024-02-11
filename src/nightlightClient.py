import sys
import requests

def parseArgs(args):
    command = args[0].lower()
    if command == "getnextsunset":
        getNextSunset()
    if command == "turnoff":
        turnOff
    
def getNextSunset():
    r = requests.get("http://127.0.0.1:5000/getNextSunset")
    time = r.json()
    print(f"Next sunset: {time}")

def turnOff():
    r = requests.get("http://127.0.0.1:5000/turnOff")
    print(r.json())

# def getUserConfig():
#     lightCount = getSettingInput("Number of lights",0)
#     plugCount =  int(getSettingInput("Number of plugs",0))
#     plugs = []
#     for _ in range(plugCount):
#         ip = input("Plug IP: ")
#         plugs.append(ShellyPy.Shelly(ip))
#     lifx = LifxLAN(lightCount)       
#     latitude = getSettingInput("Latitude", -90, 90)
#     longitude = getSettingInput("Longitude", -180, 180)
#     sunsetOffset = getSettingInput("Sunset Offset (mins)", 0, 720) # 720 mins = 12 hours
#     lightBrightness = getSettingInput("Max Brightness Setting", 0, 1)
#     lightTemperature = getSettingInput("Light Temperature (Kelvin)", 2500, 9000)
#     transitionDuration = getSettingInput("Transition Duration (sec)", 0,3600) # 3600 secs = 1 hour
                
#     return NightLightConfig(lifx.get_lights(),plugs,latitude,longitude,sunsetOffset,lightBrightness,lightTemperature,transitionDuration)

# def getSettingInput(settingName,minValue = -math.inf,maxValue = math.inf):
#     while(True):
#         settingValue = float(input(f"{settingName}: "))
#         if( minValue <= settingValue <= maxValue ):
#             return settingValue
#         else:
#             print(f"Invalid {settingName}, value must be in range {minValue} - {maxValue}")

if __name__ == '__main__':
    args = sys.argv[1:]
    parseArgs(args)