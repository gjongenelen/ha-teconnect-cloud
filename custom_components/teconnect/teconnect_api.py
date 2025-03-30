import requests
import asyncio

class TEConnectAPI:
    def __init__(self, email, password, device_token):
        self.email = email
        self.password = password
        self.auth_token = None
        self.device_token = device_token

    async def login(self):
        await asyncio.get_event_loop().run_in_executor(None, self._login_sync)

    def _login_sync(self):
        response = requests.post(
            "https://teco.thingscloud.it/api/mobile/login",
            json={"email": self.email, "password": self.password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        self.device_token = response.json().get("device_token")

    async def authenticate(self):
        if not self.device_token:
            raise ValueError("Device token not set. It should be provided via config.")
        await asyncio.get_event_loop().run_in_executor(None, self._authenticate_sync)

    def _authenticate_sync(self):
        response = requests.post(
            "https://teco.thingscloud.it/api/mobile/authenticate",
            json={"email": self.email, "token": self.device_token},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        self.auth_token = response.json().get("token")

    async def fetch_data(self):
        if not self.auth_token:
            await self.authenticate()
        return await asyncio.get_event_loop().run_in_executor(None, self._fetch_data_sync)

    def _fetch_data_sync(self):
        response = requests.get(
            "https://teco.thingscloud.it/api/devices",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}"
            }
        )
        response.raise_for_status()
        return response.json()