# Installation

## Raspberry
Install the pre-configured RPi OS image from https://docs.luxonis.com/projects/hardware/en/latest/pages/guides/raspberrypi/.
**RPi_64bit_OS.xz** works out of the box for Raspberry Pi 4 & 5.

## VSCode
Install the following plugins:
- Gitlens
- Python
- Save Typing
- Shiny

## Project setup
The project lies in the **luxonis** folder on the Desktop.
Make sure to load the whole folder into VSCode.
The virtual envrionment is also contained in that folder named: **enDepthAI** 

Additional packages need to be installed:
- `python -m pip install depthai -U` (Not sure yet it necessary: Update depthai to the latest version)
- `pip install depthai-sdk`
- `pip install fastapi` (API)
- `pip install "uvicorn[standard]"` (Backendserver)
- `pip install shiny` (Frontend)