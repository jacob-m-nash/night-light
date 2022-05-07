import numpy as np
import sunsetCalculator
def Run():
    while(True):
        while(True):
            latitude = float(input("Input latitude: "))
            if -90 <= latitude and latitude <= 90:
                break
            else:
                print("Invlad latitude, must be between -90 and 90 degrees. Please try again.")
        while(True):
            longitude = float(input("Input longitude: "))
            if -180 <= longitude and longitude <= 180:
                break
            else:
                print("Invlad longitude, must be between -180 and 180 degrees. Please try again.")
        
        sunsets = sunsetCalculator.getYearOfSunsets(latitude,longitude)

    return


if __name__ == '__main__':
    print("Running...")
    Run()

