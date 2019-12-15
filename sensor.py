"""
Meteologic Metric component for Home Assistant.
Maintainer:       Daniel Mason
Version:          v0.0.1
Documentation:    https://github.com/danobot/meteologic_metrics
Issues Tracker:   Report issues on Github. Ensure you have the latest version. Include:
                    * YAML configuration (for the misbehaving entity)
                    * log entries at time of error and at time of initialisation
"""


from homeassistant.helpers.entity import Entity
import logging
import math as m
from psypy import psySI as SI
from homeassistant.const import (TEMP_CELSIUS)
logger = logging.getLogger(__name__)

CONF_TEMP = 'temp'
CONF_HUMIDITY = 'hum'
CONF_DEW_POINT = 'dew'
CONF_PRESSURE = 'pressure'
CONF_NAME = 'name'
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([ExampleSensor(hass, config)])



class ExampleSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.hass = hass
        self.outdoorTemp = config.get(CONF_TEMP)
        self.outdoorHum = config.get(CONF_HUMIDITY)
        self.pressureSensor= config.get(CONF_PRESSURE)
        self.dewSensor = config.get(CONF_DEW_POINT)
        self.dew = None
        self.temp_out = None
        self.hum_out = None
        self.pressure = None
        self.wetBulbEstimate = None
        self.S = None
        if config.get(CONF_NAME): 
            self._name = config.get(CONF_NAME)
        else: 
            self._name = "Meteologic Metrics"
        self._state = None


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name 

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS
    def toKelvin(self, celsius):
        return celsius# + 273.15

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""

        attr = {}
        if self._name:
            attr['name'] = self._name
        if self.temp_out: 
            attr['temperature'] = self.temp_out
        if self.hum_out: 
            attr['humidity'] = self.hum_out
        if self.dew: 
            attr['dew point'] = self.dew
        if self.pressure: 
            attr['pressure (pascals)'] = self.pressure

        if self.wetBulbEstimate:
            attr["wet bulb temp estimate K"] = round(self.wetBulbEstimate, 2)
            attr["wet bulb temp estimate C"] = round(self.wetBulbEstimate-273.15, 2)
        if self.S:

            S = self.S
            attr = {
                "dry bulb temp C": round(S[0]-273.15, 2),
                "wet bulb temp C": round(S[5]-273.15, 2),
                "dry bulb temp K": round(S[0], 2),
                "wet bulb temp K": round(S[5], 2),
                "specific enthalpy": round(S[1], 2),
                "relative humidity": round(S[2], 2),
                "specific volume": round(S[3], 2),
                "humidity ratio": round(S[4], 2),
            }

        return attr


    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            logger.debug("Temp outdoor (raw sensor value): " + str(self.hass.states.get(self.outdoorTemp).state))
            logger.debug("hum outdoor (raw sensor value):  " + str(self.hass.states.get(self.outdoorHum).state))
            logger.debug("pressure (raw sensor value):     " + str(self.hass.states.get(self.pressureSensor).state))
            self.temp_out = self.toKelvin(float(self.hass.states.get(self.outdoorTemp).state))
            self.hum_out = self.toKelvin(float(self.hass.states.get(self.outdoorHum).state))
            self.pressure = round(float(self.hass.states.get(self.pressureSensor).state)*100, 2)

            logger.debug("Temp outdoor:      " + str(self.temp_out))
            logger.debug("Hum outdoor:       " + str(self.hum_out))
            logger.debug("Pressure (pascal): " + str(self.pressure))
            
            if self.dewSensor:

                logger.debug("dew (raw sensor value):     " + str(self.hass.states.get(self.dewSensor).state))
                self.dew = self.toKelvin(float(self.hass.states.get(self.dew).state))
                logger.debug("Dew (pascal): " + str(self.dew))
                self.wetBulbEstimate = self.temp_out - (self.temp_out-self.dew)/3


            S=SI.state("DBT",self.temp_out+273.15,"RH",self.hum_out/100,self.pressure)
            self.S = S
            logger.debug("The dry bulb temperature is "+ str(S[0]))
            logger.debug("The specific enthalpy is "+ str(S[1]))
            logger.debug("The relative humidity is "+ str(S[2]))
            logger.debug("The specific volume is "+ str(S[3]))
            logger.debug("The humidity ratio is "+ str(S[4]))
            logger.debug("The wet bulb temperature is "+ str(S[5]-273.15))
            
            self._state = round(S[5]-273.15, 2)
        except ValueError as e:
            logger.warning("Some input sensor values are still unavailable")

        except AttributeError:
            logger.error("Some entity does not exist or is spelled incorrectly. Did its component initialise correctly?")
    

