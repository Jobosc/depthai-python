import os
from dotenv import load_dotenv
from argparse import ArgumentParser

class ENVParser:
    def __init__(self):
        load_dotenv(dotenv_path="examples/CPDetector/.env")
        self._rgb_weight = os.getenv("RGB_WEIGHT")
        self._fps = os.getenv("FPS")
        self._video_width = os.getenv("VIDEO_WIDTH")
        self._video_height = os.getenv("VIDEO_HEIGHT")
    
    @property
    def rgb_weight(self):
        return float(self._rgb_weight)
    
    @property
    def fps(self):
        return int(self._fps)

class CMDParser:
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('-alpha', type=float, default=None, help="Alpha scaling parameter to increase float. [0,1] valid interval.")
        
        args = parser.parse_args()
        self._alpha = args.alpha

    @property
    def alpha(self):
        return self._alpha