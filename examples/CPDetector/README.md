# Installation

## Raspberry
Install the pre-configured RPi OS image from https://drive.google.com/drive/folders/1O50jPpGj_82jkAokdrsG--k9OBQfMXK5.

**OAK_CM4_POE_V9** works out of the box. I still decided to choose **OAK_CM4_POE_V10** because it's the more recent version (Just noticed one script that didn't work out of the box __rg_depth_aligned.py__)

All required packages are already installed on those images.
- Update depthai to the latest version `python -m pip install depthai -U`
- Install further requirements for frontend:
    - `pip install fastapi`
    - `pip install "uvicorn[standard]"`
    - `pip install shiny`
    - `pip install depthai-sdk`