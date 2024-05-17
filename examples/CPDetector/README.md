# Installation

## Raspberry

Install the pre-configured RPi OS image
from https://docs.luxonis.com/projects/hardware/en/latest/pages/guides/raspberrypi/.
**RPi_64bit_OS.xz** works out of the box for Raspberry Pi 4 & 5.

## VSCode

Install the following plugins:

- Gitlens
- Python
- Save Typing
- Shiny
- Black Formatter

## Project setup

1. Copy the file in `./examples/CPDetector/basic-app/.env.temp` and create an `.env` file with all the required environment
   variables

### Raspberry Pi
1. The project lies in the **luxonis** folder on the Desktop.
   Make sure to load the whole folder into VSCode.
   The virtual environment is also contained in that folder named: **envDepthAI**
   Additional packages need to be installed:
    - `pip install -r requirements.txt`

### Macbook
`curl -fL https://docs.luxonis.com/install_dependencies.sh | bash`

In case of issues displaying videos:

`python3 -m pip install opencv-python --force-reinstall --no-cache-dir`


## Run application
`python -m shiny run --port 34517 --reload --autoreload-port 43563`