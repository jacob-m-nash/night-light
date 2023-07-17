import math
import datetime
import calendar
import pytz

# Calculates the time of day the sun will set in minutes 
def calculateSunsetTime(dateTime, latitude, longitude):
    daysOfTheYear = 366 if calendar.isleap(dateTime.year) else 365 # Leap year check
    dayOfTheYear = dateTime.timetuple().tm_yday 
    fractionalYear = (2 * math.pi / daysOfTheYear) * (dayOfTheYear - 1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(fractionalYear) - 0.032077 * math.sin(fractionalYear) - 0.014615 * math.cos(2 * fractionalYear) - 0.040849 * math.sin(2 * fractionalYear))
    decl = 0.006918 - 0.399912 * math.cos(fractionalYear) + 0.070257 * math.sin(fractionalYear) - 0.006758 * math.cos(2 * fractionalYear) + 0.000907 * math.sin(2 * fractionalYear) - 0.002697 * math.cos(3 * fractionalYear) + 0.00148 * math.sin(3 * fractionalYear)
    hourAngle = - math.acos((math.cos(math.radians(90.833)) / (math.cos(math.radians(latitude)) * math.cos(decl))) - (math.tan(math.radians(latitude)) * math.tan(decl)))
    sunsetTime = 720 - 4 * (longitude +  math.degrees(hourAngle)) - eqtime
    sunsetHour = round(sunsetTime // 60)
    sunsetMinute = round(sunsetTime % 60) 
    if(sunsetHour not in range(0,24)):
        print(sunsetHour)
    if(sunsetMinute not in range(0,60)):
        print(sunsetMinute)
    return dateTime.combine(dateTime,datetime.time(sunsetHour,sunsetMinute),pytz.UTC)

def getNextSunset(latitude,longitude):
    currentDateTime = datetime.datetime.now(pytz.UTC)
    sunsetTime = calculateSunsetTime(currentDateTime,latitude,longitude)
    if(sunsetTime > currentDateTime): # if sunset time has not already passed
        return sunsetTime
    else:
        tomorrowDateTime = currentDateTime + datetime.timedelta(days=1)
        return calculateSunsetTime(tomorrowDateTime,latitude,longitude)
