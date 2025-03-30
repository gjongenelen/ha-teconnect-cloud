from datetime import timedelta
import logging
from homeassistant.components.sensor import SensorEntity
from .teconnect_api import TEConnectAPI
from .const import DOMAIN

SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_entry(hass, entry, async_add_entities):
    api = TEConnectAPI(entry.data["email"], entry.data["password"])
    data = await hass.async_add_executor_job(api.fetch_data)
    entities = [
        TEConnectSensor(api, "Current Temperature", lambda d: d["temps"]["Probe_1"]),
        TEConnectSensor(api, "Set Temperature", lambda d: d["params"]["SEt"])
    ]
    async_add_entities(entities, True)

class TEConnectSensor(SensorEntity):
    def __init__(self, api, name, value_fn):
        self.api = api
        self._name = name
        self._value_fn = value_fn
        self._state = None

    @property
    def name(self):
        return f"TEConnect {self._name}"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        data = await self.api.fetch_data()
        self._state = self._value_fn(data)