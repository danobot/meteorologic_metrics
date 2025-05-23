"""
Meteorologic Metric component for Home Assistant.
Maintainer:       Daniel Mason
Version:          v0.0.1
Documentation:    https://github.com/danobot/meteorologic_metrics
Issues Tracker:   Report issues on Github. Ensure you have the latest version. Include:
                    * YAML configuration (for the misbehaving entity)
                    * log entries at time of error and at time of initialisation
"""

from homeassistant.helpers.entity import Entity
import logging
import math as m
from psypy import psySI as SI
from .helpers import *
from homeassistant.const import UnitOfTemperature
logger = logging.getLogger(__name__)

from .const import *


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([ClimateMetricsSensor(hass, config)])



class ClimateMetricsSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.hass = hass
        self.outdoorTemp = config.get(CONF_TEMP)
        self.outdoorHum = config.get(CONF_HUMIDITY)
        self.pressureSensor= config.get(CONF_PRESSURE)

        self.dewSensor = config.get(CONF_DEW_POINT)
        self.dew_temp_k = None
        self.dew_temp_estimate_c = None
        self.temp_out_k = None
        self.hum_out = None
        self.pressure = None
        self.comfort_level = None
        self.heat_index = None
        self.web_bulb_dew = None
        self.wet_bulb_stull = None
        self.relative_humidity = None
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
        return UnitOfTemperature.CELSIUS


    @property
    def extra_state_attributes(self):
        attr = {}

        if self.S:

            S = self.S
            self.relative_humidity = S[2]
            attr = {
                "SI dry bulb temp C": round(toC(S[0]), 2),
                "SI wet bulb temp C": round(toC(S[5]), 2),
                "SI specific enthalpy": round(S[1], 2),
                "SI relative humidity": round(S[2], 2),
                "SI specific volume": round(S[3], 2),
                "SI humidity ratio": round(S[4], 2)
            }

        if self.temp_out_k:
            attr['temperature'] = round(toC(self.temp_out_k), 2)
        if self.hum_out:
            attr['humidity'] = self.hum_out
        if self.dew_temp_k:
            attr['dew point'] = toC (self.dew_temp_k)
        if self.dew_temp_estimate_c:
            attr['dew point estimate'] = round(self.dew_temp_estimate_c, 2)
        if self.pressure:
            attr['pressure (pascals)'] = self.pressure
        if self.heat_index:
            attr['heat index'] = self.heat_index

        if self.web_bulb_dew:
            attr["wet bulb temp (dew estimate) C"] = round(toC(self.web_bulb_dew), 2)

        if self.wet_bulb_stull:
            attr["wet bulb temp stull estimate C"] = round(self.wet_bulb_stull, 2)

        if self.comfort_level:
            attr["comfort level "] = self.comfort_level
            attr["comfort level info"] = COMFORT[self.comfort_level]


        return attr

    def _outdoor_temp(self):
        return float(self.hass.states.get(self.outdoorTemp).state)

    def _pressure(self):
        """ pressure in millibar == hectopascal == pascal / 100 """
        return float(self.hass.states.get(self.pressureSensor).state)

    def _outdoor_hum(self):
        return float(self.hass.states.get(self.outdoorHum).state)

    def _dew_temp(self):
        return float(self.hass.states.get(self.dewSensor).state)

    def update(self):
        if not self._data_available():
            return False
        try:
            self.temp_out_k = toK(self._outdoor_temp())
            self.hum_out = self._outdoor_hum()

            self.pressure = self._pressure()*100 # convert hectopascal to pascal

            logger.debug("Temp outdoor (K):      " + str(self.temp_out_k))
            logger.debug("Hum outdoor (K):       " + str(self.hum_out))
            logger.debug("Pressure (pascal): " + str(self.pressure))

            if self.dewSensor:

                self.dew_temp_k = self._dew_temp()
                logger.debug("dew (raw sensor value):     " + str(self.dew_temp_k))
                logger.debug("Dew (C): " + str(self.dew_temp_k))
                self.web_bulb_dew = round(self.temp_out_k - (self.temp_out_k-self.dew_temp_k)/3, 2)
                logger.debug("Wet bulb dewpoint depression (C): " + str(self.web_bulb_dew))
                self.comfort_level = self.determine_comfort(toC(self.dew_temp_k))
            else:
                self.dew_temp_estimate_c = self.calculate_dewpoint(self.temp_out_k, self.hum_out)
                self.comfort_level = self.determine_comfort(toC(self.dew_temp_estimate_c))


            S=SI.state("DBT", self.temp_out_k,"RH", self.hum_out/100, self.pressure)
            self.S = S
            logger.debug("SI Results ================================ START")
            logger.debug("The dry bulb temperature is "+ str(S[0]))
            logger.debug("The specific enthalpy is "+ str(S[1]))
            logger.debug("The relative humidity is "+ str(S[2]))
            logger.debug("The specific volume is "+ str(S[3]))
            logger.debug("The humidity ratio is "+ str(S[4]))
            logger.debug("The wet bulb temperature is "+ str(toC(S[5])))
            logger.debug("SI Results ================================ END")
            self._state = round(toC(S[5]), 2)

            self.wet_bulb_stull = self.calculate_wb_stull()
            logger.debug("The wet bulb temperature (Stull formulat)) "+ str(self.wet_bulb_stull))

            self.heat_index = self.calculate_heat_index(self.temp_out_k, self.hum_out)
            logger.debug("Heat index "+ str(self.heat_index))

        except ValueError as e:
            logger.warning("Some input sensor values are still unavailable")

        except AttributeError:
            logger.error("Some entity does not exist or is spelled incorrectly. Did its component initialise correctly?")
        except Exception as e:
            logger.error(e)

    @property
    def available(self):
        return self._data_available()

    def _data_available(self):
        d = [
            self.outdoorHum, self.outdoorTemp, self.pressureSensor, self.dewSensor
        ]

        for s in d:
            if s:
                state = self.hass.states.get(s)
                if state is None:
                    return False
                if state.state == 'unknown':
                    return False
        return True


    def calculate_heat_index(self, temp_k, hum) -> float:
        """
        https://en.wikipedia.org/wiki/Heat_index
        The formula below approximates the heat index in degrees Fahrenheit, to within ±1.3 °F (0.7 °C). It is the result of a multivariate fit (temperature equal to or greater than 80 °F (27 °C) and relative humidity equal to or greater than 40%) to a model of the human body.[1][13] This equation reproduces the above NOAA National Weather Service table (except the values at 90 °F (32 °C) & 45%/70% relative humidity vary unrounded by less than ±1, respectively).
        Params: temperature in Kelvin, and humidity as a percentage
        """



        if temp_k and hum:
            T = KtoF(temp_k)
            R = hum
            if T > 80 and R > 40:
                hi = c1 + c2*T + c3*R + c4*T*R + c5*m.pow(T, 2) + c6*m.pow(R, 2) + c7*m.pow(T, 2)*R + c8*m.pow(R, 2)*T + c9*m.pow(T, 2)*m.pow(R, 2)
                return FtoC(hi)

        return None

    def calculate_dewpoint(self, temp_out_k, hum_out) -> float:
        if temp_out_k and hum_out:
            alpha = m.log(hum_out / 100) + (AA*toC(temp_out_k))/(BB+toC(temp_out_k))
            dp = (BB*alpha) / (AA - alpha)
            logger.debug("Dew Point Estimate (C): " + str(dp))
            return dp
        return None

    @property
    def icon(self):
        """Return the entity icon."""
        if self.comfort_level == 0:
            return "mdi:emoticon-excited-outline"
        if self.comfort_level == 1:
            return "mdi:emoticon-outline"
        if self.comfort_level == 2:
            return "mdi:emoticon-happy-outline"
        if self.comfort_level == 3:
            return "mdi:emoticon-neutral-outline"
        if self.comfort_level == 4:
            return "mdi:emoticon-sad-outline"
        return "mdi:circle-outline"

    def determine_comfort(self, dp):

        if dp > 21:
            comfort_level = 4
        if dp > 18:
            comfort_level = 3
        if dp > 16:
            comfort_level = 2
        if dp > 10:
            comfort_level = 1
        if dp <= 10:
            comfort_level = 0

        return comfort_level
    def calculate_wb_stull(self) -> float:
        """
            Although many equations have been created over the years our calculator uses the Stull formula,
            which is accurate for relative humidities between 5% and 99% and temperatures between -20°C and 50°C.
            It loses its accuracy in situations where both moisture and heat are low in value, but even then the error range is only between -1°C to +0.65°C.
            Source: https://www.omnicalculator.com/physics/wet-bulb
        """
        T = toC(self.temp_out_k)
        H = self.hum_out
        if H > 5 and H < 99 and T > -20 and T < 50:
            return T * m.atan(0.151977 * m.pow(H + 8.313659, 0.5)) + m.atan(T + H) - m.atan(H - 1.676331) + 0.00391838 * m.pow(H, 3/2) * m.atan(0.023101 * H) - 4.686035
        return None
