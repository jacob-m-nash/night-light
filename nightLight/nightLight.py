import math
import datetime


def calculateSunset(date,latitude,longitude):
    dayOfTheYear = date.timetuple().tm_yday
    sunsetTime = calculateSunsetTime(dayOfTheYear,latitude,longitude)
    test = date.replace(hour= sunsetTime.hour, minute = sunsetTime.minute)

    return test


# Calculates the time of day the sun will set in minutes 
def calculateSunsetTime(dayOfTheYear, latitude, longitude) : 
    fractionalYear = (2 * math.pi / 360) * (dayOfTheYear -1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(fractionalYear) - 0.032077 * math.sin(fractionalYear) - 0.014615 * math.cos(2 * fractionalYear) - 0.040849 * math.sin(2 * fractionalYear))
    decl = 0.006918 - 0.399912 * math.cos(fractionalYear) + 0.070257 * math.sin(fractionalYear) - 0.006758 * math.cos(2 * fractionalYear) + 0.000907 * math.sin(2 * fractionalYear) - 0.002697 * math.cos(3 * fractionalYear) + 0.00148 * math.sin(3 * fractionalYear)
    hourAngle = - math.acos((math.cos(math.radians(90.833)) / (math.cos(math.radians(latitude)) * math.cos(decl))) - (math.tan(math.radians(latitude)) * math.tan(decl)))
    sunsetTime = 720 - 4 * (longitude +  math.degrees(hourAngle)) - eqtime
    sunsetHour = round(sunsetTime // 60)
    sunsetMinute = round(sunsetTime % 60) #todo find out why we are a couple of mins off each time 
    return datetime.time(sunsetHour,sunsetMinute)
