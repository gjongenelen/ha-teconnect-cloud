from datetime import timedelta
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.components.binary_sensor import BinarySensorEntity
from .teconnect_api import TEConnectAPI
from .const import DOMAIN

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
    api = TEConnectAPI(entry.data["email"], entry.data["password"], entry.data["device_token"])
    data = await hass.async_add_executor_job(api.fetch_data)
    entities = [
        TEConnectSensor(api, "Current Temperature", lambda d: d["data"][0]["temps"]["Probe_1"] / 10, "temp_probe_1", "°C"),
        TEConnectSensor(api, "Set Temperature", lambda d: d["data"][0]["params"]["SEt"] / 10, "set_temp", "°C"),
        TEConnectSensor(api, "Hysteresis", lambda d: d["data"][0]["params"]["Hy"] / 10, "hysteresis", "°C"),
        TEConnectBinarySensor(api, "Defrost", lambda d: d["data"][0]["status"]["Defrost"] == 1, "defrost_active"),
        TEConnectBinarySensor(api, "Cooling", lambda d: d["data"][0]["status"]["Cooling"] == 1, "cooling_active"),
        TEConnectBinarySensor(api, "Heating", lambda d: d["data"][0]["status"]["Aux"] == 1, "heating_active")
    ]
    async_add_entities(entities, True)

class TEConnectSensor(SensorEntity):
    def __init__(self, api, name, value_fn, unique_id, unit):
        self.api = api
        self._name = name
        self._value_fn = value_fn
        self._state = None
        self._unique_id = unique_id
        self._unit = unit

    @property
    def name(self):
        return f"TEConnect {self._name}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "teconnect_device")},
            "name": "TECOnnect",
            "manufacturer": "TECO",
            "model": "Chiller",
        }

    @property
    def unit_of_measurement(self):
        return self._unit

    async def async_update(self):
        data = await self.api.fetch_data()
        self._state = self._value_fn(data)

class TEConnectBinarySensor(BinarySensorEntity):
    def __init__(self, api, name, value_fn, unique_id):
        self.api = api
        self._name = name
        self._value_fn = value_fn
        self._state = None
        self._unique_id = unique_id

    @property
    def is_on(self):
        return self._state

    @property
    def name(self):
        return f"TEConnect {self._name}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "teconnect_device")},
            "name": "TECOnnect",
            "manufacturer": "TECO",
            "model": "Chiller",
        }

    async def async_update(self):
        data = await self.api.fetch_data()
        self._state = self._value_fn(data)