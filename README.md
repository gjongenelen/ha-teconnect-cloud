# ha-teconnect

Integrate your TECO aquarium chiller (and heater) into Home-assistant

## Install
Copy contents of custom_components folder to your home-assistant config/custom_components folder or install through HACS. After reboot of Home-Assistant, this integration can be configured through the integration setup UI

## Setup
1. Login with your Teconnect account
2. Your devices are retrieved from the cloud
3. You need to login again (reconfigure integration) if you add a new device to your account

## Features
- Climate control (get/set target and current temperature)
- Get/set hysteresis
- That's it for now... PR's are welcome

## Requirements
- Home Assistant 2023.0 or newer
- A TECO account

## License
See `LICENSE`.

## Disclaimer
Not affiliated with or endorsed by TECO.
