# night-light :bulb:
 An application for automatically turning on a smart bulb at sunset. 

# Sunset calculations
 To calculate the sunset at a given location on a given calender we can use [NOAA's General Solar Position Calculations.](https://gml.noaa.gov/grad/solcalc/solareqns.PDF) 

 The first step is to calculate the the fractional year (γ) in radians. This is done using the formula:

 $$\gamma = \frac{2 \pi}{365} * (\mathrm{day of year} - 1 + \frac{\mathit{hour} - 12}{24})$$

 Using the $\gamma$ we can now estimate the equation of time (*eqtime*) in minutes  and solar declination angle (*decl*) in radians using the formulas below:

$$ \mathit{eqtime} = 229.18 * (0.000075 + 0.001868 \cos(\gamma) – 0.032077 \sin(\gamma) – 0.014615 \cos(2 \gamma) – 0.040849 \sin(2 \gamma)) $$

$$ \mathit{decl} = 0.006918 – 0.399912 \cos(\gamma) + 0.070257 \sin(\gamma) – 0.006758 \cos(2 \gamma) \\ + 0.000907 sin(2 \gamma) – 0.002697 \cos(3 \gamma) + 0.00148 \sin(3 \gamma) $$

Finlay we can calculate the hour angle (ha) when the solar zenith is 90.833° and then use all calculations to estimate the sunset time in minutes:

$$\mathit{ha} = \pm\arccos(\frac{\cos(90.833)}{\cos(\mathit{lat}) \cos(\mathit{decl})} - \tan(\mathit{lat}) \tan(\mathit{decl}))$$

*Note: To calculate the sunset hour angle we use the negative hour angle.* 

$$\mathit{sunrise/sunset} = 720 - 4 * (\mathit{longitude} + \mathit{ha}) - \mathit{eqtime}$$
