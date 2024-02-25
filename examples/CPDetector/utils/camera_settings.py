import depthai as dai
from utils.parser import ENVParser, CMDParser


class CameraSettings:
    def __init__(self):
        env_parser = ENVParser()
        cmd_parser = CMDParser()

        # Weights to use when blending depth/rgb image (should equal 1.0)
        self.rgbWeight = env_parser.rgb_weight
        self.depthWeight = env_parser.depth_weight

        # Camera parameters
        self.fps = env_parser.fps
        self.video_width = env_parser.video_width
        self.video_height = env_parser.video_height
        self.alpha = cmd_parser.alpha

        # The disparity is computed at this resolution, then upscaled to RGB resolution
        self.monoResolution = dai.MonoCameraProperties.SensorResolution.THE_720_P

        # Properties
        self.rgbCamSocket = dai.CameraBoardSocket.CAM_A

        # Pipeline Parameters
        self._pipeline = dai.Pipeline()
        self._device = dai.Device()
        self._stereo = None
    
    @property
    def pipeline(self):
        return self._pipeline
    
    @property
    def device(self):
        return self._device
    
    @property
    def stereo(self):
        return self._stereo

    def setup_pipeline(self):
        # Create pipeline
        queueNames = []

        # Define sources and outputs
        camRgb = self._pipeline.create(dai.node.Camera)
        monoLeft = self._pipeline.create(dai.node.MonoCamera)
        monoRight = self._pipeline.create(dai.node.MonoCamera)
        stereo = self._pipeline.create(dai.node.StereoDepth)

        rgbOut = self._pipeline.create(dai.node.XLinkOut)
        disparityOut = self._pipeline.create(dai.node.XLinkOut)

        rgbOut.setStreamName("rgb")
        queueNames.append("rgb")
        disparityOut.setStreamName("disp")
        queueNames.append("disp")

        camRgb.setBoardSocket(self.rgbCamSocket)
        camRgb.setSize(self.video_width, self.video_height)
        camRgb.setFps(self.fps)

        # For now, RGB needs fixed focus to properly align with depth.
        # This value was used during calibration
        try:
            calibData = self._device.readCalibration2()
            lensPosition = calibData.getLensPosition(self.rgbCamSocket)
            if lensPosition:
                camRgb.initialControl.setManualFocus(lensPosition)
        except:
            raise
        monoLeft.setResolution(self.monoResolution)
        monoLeft.setCamera("left")
        monoLeft.setFps(self.fps)
        monoRight.setResolution(self.monoResolution)
        monoRight.setCamera("right")
        monoRight.setFps(self.fps)

        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        # LR-check is required for depth alignment
        stereo.setLeftRightCheck(True)
        stereo.setDepthAlign(self.rgbCamSocket)

        # Linking
        camRgb.video.link(rgbOut.input)
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)
        stereo.disparity.link(disparityOut.input)

        camRgb.setMeshSource(dai.CameraProperties.WarpMeshSource.CALIBRATION)
        if self.alpha is not None:
            camRgb.setCalibrationAlpha(self.alpha)
            stereo.setAlphaScaling(self.alpha)
        
        self._stereo = stereo