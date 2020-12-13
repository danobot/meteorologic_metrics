This component calculates psychrometric states of moist air using ASHRAE 2009 Fundamentals formulations. Atmospheric pressure, and humidity must be given to calculate the other propreties.

The state properties include:

* dry bulb temperature (DBT), 
* specific enthalpy (H), 
* relative humidity (RH), 
* specific volume (V), 
* humidity ratio (W), 
* and wet bulb temperature (WBT)
* wet bulb temperature (estimate from dewpoint depression)
* wet bulb temperature (stull formula)

## Multiple Wet Bulb Temperature Estimations

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