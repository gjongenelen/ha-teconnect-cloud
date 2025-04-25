import asyncio

import aiohttp


class TEConnectData:
    def __init__(self, data: dict):
        self._data = data

    def get_for_device(self, id: int):
        for device in self._data:
            if device["id"] == id:
                return device
        return None

    def get_all(self):
        return self._data


class TEConnectAPI:
    def __init__(self, email, device_token):
        self.email = email
        self.auth_token = None
        self.device_token = device_token
        self._auth_time = None

    async def login(self, password):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://teco.thingscloud.it/api/mobile/login",
                    json={
                        "email": self.email,
                        "password": password
                    },
                    headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self.device_token = data.get("device_token")
                return self.device_token

    async def ensure_authenticated(self):
        if not self.device_token:
            raise ValueError("Device token not set. It should be provided via config.")
        if not self.auth_token or (self._auth_time and asyncio.get_event_loop().time() - self._auth_time > 3600):
            await self.authenticate()

    async def authenticate(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://teco.thingscloud.it/api/mobile/authenticate",
                    json={"email": self.email, "token": self.device_token},
                    headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self.auth_token = data.get("token")
                return self.auth_token

    async def fetch_data(self):
        await self.ensure_authenticated()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://teco.thingscloud.it/api/devices",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.auth_token}"
                    }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return TEConnectData(data["data"])

    async def set_temperature(self, device_id: int, value: int):
        await self.ensure_authenticated()

        setpoint = int(value * 10)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"https://teco.thingscloud.it/api/devices/{device_id}/setpoint",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.auth_token}"
                    },
                    json={"setpoint": setpoint}
            ) as response:
                response.raise_for_status()
                return

    async def set_hysteresis(self, device_id, value):
        return True
    # await self._send_command(device_id, {"Hy": rounded})
