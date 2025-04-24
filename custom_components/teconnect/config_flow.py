import logging

import voluptuous as vol
from homeassistant import config_entries

from .teconnect_api import TEConnectAPI

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN


class TEConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str,
            }), errors=errors)

        api = TEConnectAPI(user_input["email"], None)
        device_token = await api.login(user_input["password"])

        await api.authenticate()

        data = await api.fetch_data()

        devices = []
        for device in data.get_all():
            devices.append({
                "teco_id": device["id"],
                "name": device["name"],
                "model": device["type"],
                "serial_number": device["serial"]
            })

        return self.async_create_entry(
            title=user_input["email"],
            data={
                "email": user_input["email"],
                "device_token": device_token,
                "devices": devices,
            },
        )
