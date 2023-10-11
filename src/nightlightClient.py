import os
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
    test = r.json()
    print(test)

def turnOff():
    r = requests.get("http://127.0.0.1:5000/turnOff")

if __name__ == '__main__':
    args = sys.argv[1:]
    parseArgs(args)