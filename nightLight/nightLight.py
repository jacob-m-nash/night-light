import math

# Calculates the time of day the sun will set in minutes 
def calculateSunset(dayOfTheYear, latitude, longitude) : 
    fractionalYear = (2 * math.pi / 360) * (dayOfTheYear - 1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(fractionalYear) - 0.032077 * math.sin(fractionalYear) - 0.014615 * math.cos(2 * fractionalYear) - 0.040849 * math.sin(2 * fractionalYear))
    decl = 0.006918 - 0.399912 * math.cos(fractionalYear) + 0.070257 * math.sin(fractionalYear) - 0.006758 * math.cos(2 * fractionalYear) + 0.000907 * math.sin(2 * fractionalYear) - 0.002697 * math.cos(3 * fractionalYear) + 0.00148 * math.sin(3 * fractionalYear)  
    hourAngle = - math.acos((math.cos(math.radians(90.833)) / (math.cos(latitude) * math.cos(decl))) - (math.tan(latitude) * math.tan(decl)))
    sunset = 720 - 4 * (longitude +  math.degrees(hourAngle)) - eqtime
    return sunset

#1st jan london sunset: 16:02
print(calculateSunset(1,51.5,-0.13))
