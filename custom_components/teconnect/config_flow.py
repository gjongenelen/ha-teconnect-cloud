import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .teconnect_api import TEConnectAPI

from .const import DOMAIN

class TEConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api = TEConnectAPI(user_input["email"], user_input["password"])
            await api.login()
            return self.async_create_entry(
                title="TEConnect",
                data={
                    "email": user_input["email"],
                    "password": user_input["password"],
                    "device_token": api.device_token
                }
            )

        data_schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("password"): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)