import asyncio
import logging
from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .teconnect_api import TEConnectAPI

PLATFORMS = ["climate", "number"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = TEConnectAPI(entry.data["email"], entry.data["device_token"])
    await api.authenticate()
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "entities": [],
    }
    stop_event = asyncio.Event()

    async def poll_data():
        while not stop_event.is_set():
            try:
                data = await api.fetch_data()
                _LOGGER.info("Fetched data successfully, %s", data)
                for entity in hass.data[DOMAIN][entry.entry_id]["entities"]:
                    await entity.handle_api_data(data)
            except Exception as e:
                _LOGGER.warning("Failed to fetch_data: %s", e)
            await asyncio.sleep(15)

    task = asyncio.create_task(poll_data())

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "entities": [],
        "stop_event": stop_event,
        "task": task,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    data = hass.data[DOMAIN].pop(entry.entry_id)
    data["stop_event"].set()
    data["task"].cancel()
    try:
        await data["task"]
    except asyncio.CancelledError:
        pass
    return True
