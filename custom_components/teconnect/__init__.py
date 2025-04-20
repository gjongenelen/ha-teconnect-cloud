from .const import DOMAIN

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"),
        hass.config_entries.async_forward_entry_setup(entry, "climate")
    )
    return True

async def async_unload_entry(hass, entry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_unload(entry, "sensor"),
        hass.config_entries.async_forward_entry_unload(entry, "climate")
    )
    return True