import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    entities = []
    for device in entry.data["devices"]:
        entity = TEConnectClimate(api, "Control", device)
        hass.data[DOMAIN][entry.entry_id]["entities"].append(entity)
        entities.append(entity)

    async_add_entities(entities)


class TEConnectClimate(ClimateEntity):
    def __init__(self, api, name, device):
        self.device_config = device
        self.api = api

        self._attr_unique_id = f"{device['serial_number']}"
        self.name = name

        self._target_temperature = None
        self._current_temperature = None
        self._hvac_mode = HVACMode.OFF
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._teco_device_id = id
        self._attr_min_temp = 20
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 0.1

    @property
    def temperature_unit(self):
        return "°C"

    @property
    def hvac_mode(self):
        return self._hvac_mode

    @property
    def hvac_modes(self):
        return [HVACMode.COOL, HVACMode.HEAT, HVACMode.OFF]

    @property
    def target_temperature(self):
        return self._target_temperature

    @property
    def current_temperature(self):
        return self._current_temperature

    @property
    def supported_features(self):
        return self._attr_supported_features

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_config["serial_number"])},
            "name": self.device_config["name"],
            "model": self.device_config["model"],
            "manufacturer": "TECO",
        }

    async def handle_api_data(self, data):
        data = data.get_for_device(self.device_config["teco_id"])

        if data["status"]["Aux"] == 1:
            self._hvac_mode = HVACMode.HEAT
        elif data["status"]["Cooling"] == 1:
            self._hvac_mode = HVACMode.COOL
        else:
            self._hvac_mode = HVACMode.OFF

        self._current_temperature = data["temps"]["Probe_1"] / 10
        self._target_temperature = data["params"]["SEt"] / 10

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get("temperature")
        if temp is not None:
            await self.api.set_temperature(self.device_config["teco_id"], temp)
            self._target_temperature = temp
            self.async_write_ha_state()
