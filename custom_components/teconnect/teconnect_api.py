import requests
import asyncio

class TEConnectAPI:
    def __init__(self, email, password, device_token):
        self.email = email
        self.password = password
        self.auth_token = None
        self.device_token = device_token
        self._auth_time = None

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
        self._auth_time = asyncio.get_event_loop().time()

    def _authenticate_sync(self):
        response = requests.post(
            "https://teco.thingscloud.it/api/mobile/authenticate",
            json={"email": self.email, "token": self.device_token},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        self.auth_token = response.json().get("token")

    async def fetch_data(self):
        if not self.auth_token or (self._auth_time and asyncio.get_event_loop().time() - self._auth_time > 3600):
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

    async def set_temperature(self, device_id: int, value: float):
        if not self.auth_token or (self._auth_time and asyncio.get_event_loop().time() - self._auth_time > 3600):
            await self.authenticate()
        await asyncio.get_event_loop().run_in_executor(None, self._set_temperature_sync, device_id, value)

    def _set_temperature_sync(self, device_id: int, value: float):
        setpoint = int(value * 10)
        response = requests.post(
            f"https://teco.thingscloud.it/api/devices/{device_id}/setpoint",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}"
            },
            json={"setpoint": setpoint}
        )
        response.raise_for_status()