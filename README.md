# night-light :bulb:
An application for automatically turning on a smart bulb at. sunset 
## Sunset calculation
 To calculate the sunset we can use [NOAA's General Solar Position Calculations.](https://gml.noaa.gov/grad/solcalc/solareqns.PDF) 

 The first step is to calculate the the fractional year (γ) in radians. This is done using the formula:

 ![alt text](assets\readme\fractional-year-formula.png "Fractional year formula") \
 *Note: This equation uses 12-hour time. For out use case we can use 12am for the start of the day.* 


 Using the γ we can now estimate the equation of time (*eqtime*) in minutes  and solar declination angle (*decl*) in radians using the formulas below:

 ![alt text](assets\readme\eqtime-and-decl-formulas.png "eqtime and decl formulas")

 

 
