import requests

class TEConnectAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.auth_token = None
        self.device_token = None

    def login(self):
        response = requests.post(
            "https://teco.thingscloud.it/api/mobile/login",
            json={"email": self.email, "password": self.password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        self.device_token = response.json().get("device_token")

    def authenticate(self):
        if not self.device_token:
            self.login()
        response = requests.post(
            "https://teco.thingscloud.it/api/mobile/authenticate",
            json={"email": self.email, "token": self.device_token},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        self.auth_token = response.json().get("token")

    def fetch_data(self):
        if not self.auth_token:
            self.authenticate()
        response = requests.get(
            "https://teco.thingscloud.it/api/devices/846",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}"
            }
        )
        response.raise_for_status()
        return response.json()