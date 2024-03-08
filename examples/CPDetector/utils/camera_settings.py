import depthai as dai
from utils.parser import ENVParser, CMDParser
from utils.rgb_settings import RGBSettings as rgbSettings
from utils.depth_settings import DepthSettings as depthSettings

class CameraSettings:
    def __init__(self):
        env_parser = ENVParser()
        cmd_parser = CMDParser()

        # Camera parameters
        self.fps = env_parser.fps
        self.alpha = cmd_parser.alpha
        
        # Pipeline Parameters
        self._pipeline = dai.Pipeline()
        self._stereo = None

    @property
    def pipeline(self):
        return self._pipeline
    
    @property
    def maxDisparity(self):
        return self._stereo.initialConfig.getMaxDisparity()

    def setup_pipeline(self):
        ## Create pipelines
        # Setup RGB Pipeline
        rgb = rgbSettings(self._pipeline, self.fps)
        rgb.setup_pipeline()
        self._pipeline = rgb.pipeline
        # Setup Depth Pipeline
        depth = depthSettings(self._pipeline, self.fps)
        depth.setup_pipeline()
        self._pipeline = depth.pipeline
        self._stereo = depth.stereo
