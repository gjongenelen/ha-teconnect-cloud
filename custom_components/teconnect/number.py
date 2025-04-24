import logging
from homeassistant.components.number import NumberEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    entities = []

    for device in entry.data["devices"]:
        entity = TecoHysteresisNumber(api, "Hysteresis", device)
        hass.data[DOMAIN][entry.entry_id]["entities"].append(entity)
        entities.append(entity)

    async_add_entities(entities)


class TecoHysteresisNumber(NumberEntity):
    def __init__(self, api, name, device):
        self.device_config = device
        self.api = api
        self._attr_unique_id = f"{device['serial_number']}_hy"
        self.name = name
        self._attr_native_value = None
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 2.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_config["serial_number"])},
            "name": self.device_config["name"],
            "model": self.device_config["model"],
            "manufacturer": "TECO",
        }

    async def handle_api_data(self, data, silent=False):
        data = data.get_for_device(self.device_config["teco_id"])

        self._attr_native_value = data["params"]["Hy"] / 10

        if not silent:
            self.async_write_ha_state()

    async def async_set_native_value(self, value: float):
        await self.api.set_hysteresis(self.device_config["teco_id"], value)
        self._attr_native_value = value
        self.async_write_ha_state()
