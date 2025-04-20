from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from .teconnect_api import TEConnectAPI
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    api = TEConnectAPI(entry.data["email"], entry.data["password"], entry.data["device_token"])
    async_add_entities([TEConnectClimate(api, "Climate", "climate_control")])

class TEConnectClimate(ClimateEntity):
    def __init__(self, api, name, unique_id):
        self.api = api
        self._name = name
        self._unique_id = unique_id
        self._hvac_mode = HVACMode.COOL
        self._target_temperature = None
        self._current_temperature = None
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

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
            "identifiers": {(DOMAIN, "teconnect_device")},
            "name": "TECOnnect",
            "manufacturer": "TECO",
            "model": "Chiller",
        }

    async def async_update(self):
        data = await self.api.fetch_data()
        if data["data"][0]["status"]["Aux"] == 1:
            self._hvac_mode = HVACMode.HEAT
        elif data["data"][0]["status"]["Cooling"] == 1:
            self._hvac_mode = HVACMode.COOL
        else:
            self._hvac_mode = HVACMode.OFF
        self._current_temperature = data["data"][0]["temps"]["Probe_1"] / 10
        self._target_temperature = data["data"][0]["params"]["SEt"] / 10

    async def async_set_hvac_mode(self, hvac_mode):
        self._hvac_mode = hvac_mode

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get("temperature")
        if temp is not None:
            self._target_temperature = temp
