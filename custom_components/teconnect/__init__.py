from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    await hass.config_entries.async_forward_entry_setup(entry, "climate")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # unload_ok_sensor = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    unload_ok_climate = await hass.config_entries.async_forward_entry_unload(entry, "climate")
    return unload_ok_sensor and unload_ok_climate