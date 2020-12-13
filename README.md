This component calculates psychrometric states of moist air using ASHRAE 2009 Fundamentals formulations. Atmospheric pressure, and humidity must be given to calculate the other propreties.

The entity attributes include:

* dry bulb temperature
* specific enthalpy
* relative humidity
* specific volume
* humidity ratio
* heat index
* dew point (if `dew` sensor not supplied)
* wet bulb temperature
* wet bulb temperature (estimation using dewpoint depression)
* wet bulb temperature (estimation using stull formula)

## Dew Point Calculation

If the `dew` sensor is not supplied, the component calculates an estimate for dew point (°C) using the Magnus-Tetens formula. This produces accurate results (with an uncertainty of 0.35°C) for temperatures ranging from -45°C to 60°C.

Source: https://www.omnicalculator.com/physics/dew-point

## Heat Index (Feels like temp)
Attribute name: `heat index`

> The formula below approximates the heat index in degrees Fahrenheit, to within ±1.3 °F (0.7 °C). It is the result of a multivariate fit (temperature equal to or greater than 80 °F (27 °C) and relative humidity equal to or greater than 40%) to a model of the human body. This equation reproduces the above NOAA National Weather Service table (except the values at 90 °F (32 °C) & 45%/70% relative humidity vary unrounded by less than ±1, respectively).
Source: https://en.wikipedia.org/wiki/Heat_index

The heat index represents the apparent temperature (feels like). It will only be calculated for temperatures above 27C and humidty over 40%.

## Wet Bulb Temperature Estimations

### ASHRAE 2009 Fundamentals Calculation

Attibute name: `SI wet bulb temp C`

Psychrometric states of moist air are calculated using ASHRAE 2009 Fundamentals formulations implemented in the [`psypy` package](https://pypi.org/project/psypy/)

### Dewpoint Depression estimate

Attribute name: `wet bulb temp (dew estimate) C`

This estimate using [the 1/3 rule](https://www.theweatherprediction.com/habyhints/170/)
The 1/3 rule works quite well for temperatures between -1.1C and 15.5C. For warmer temperatures than 15.5C, the cooling is between about 1/3 and 1/2 the dewpoint depression.

### Stull Estimate
Attribute name: `wet bulb temp stull estimate C`
> Although many equations have been created over the years our calculator uses the Stull formula, which is accurate for relative humidities between 5% and 99% and temperatures between -20°C and 50°C. It loses its accuracy in situations where both moisture and heat are low in value, but even then the error range is only between -1°C to +0.65°C.
Source: https://www.omnicalculator.com/physics/wet-bulb



## Configuration

```yaml
sensors:
  - platform: meteologic_metrics
    name: "Meteologic Metrics"              # optional, use if you want to use mulitple instances
    temp: sensor.outside_temp               # celsius
    hum: sensor.outside_hum                 # celsius
    dew: sensor.bom_perth_dew_point_c       # required if you want WBT estimated with dewpoint depression
    pressure: sensor.bom_perth_pressure_mb  # millibar == hectopascal == pascal * 100
```