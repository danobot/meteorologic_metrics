This component calculates psychrometric states of moist air using ASHRAE 2009 Fundamentals formulations. Atmospheric pressure, and humidity must be given to calculate the other propreties.

![Entity Attributes](entity.png)

The state properties include:

* dry bulb temperature (DBT), 
* specific enthalpy (H), 
* relative humidity (RH), 
* specific volume (V), 
* humidity ratio (W), 
* and wet bulb temperature (WBT)
* wet bulb temperature (estimate from dewpoint depression - using [the 1/3 rule](https://www.theweatherprediction.com/habyhints/170/))

# Configuration

```yaml
sensors:
  - platform: meteologic_metrics
    name: "Meteologic Metrics"              # optional, use if you want to use mulitple instances
    temp: sensor.outside_temp               # required, celsius
    hum: sensor.outside_hum                 # required, celsius
    dew: sensor.bom_perth_dew_point_c       # required if you want WBT estimated with dewpoint depression
    pressure: sensor.bom_perth_pressure_mb  # required, atmospheric pressure in millibar == hectopascal == pascal * 100
```

**Note:** The pressure value is the atmospheric pressure. You can get this from many `weather` components such as `bom` (Bureau of Meterology in Australia) and `bluesky` (global). The dew point value can be retrieved from those weather stations as well, but is not strictly required. You only need to supply it if you want to use the alternative way of calculating wet bulb temperature which is an estimate basted on dewpoint depression. (less accurate, but interesting for comparions).