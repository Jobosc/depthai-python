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
        self.resolution = dai.ColorCameraProperties.SensorResolution.THE_800_P # Resolution is set as close as possible to Yolov8 input size (YOLOv8x-pose-p6: size=1280)

        # The disparity is computed at this resolution, then upscaled to RGB resolution
        self.monoResolution = dai.MonoCameraProperties.SensorResolution.THE_800_P

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

        ## Define sources and outputs
        # Displaying channels
        camRgb = self._pipeline.create(dai.node.ColorCamera)
        monoLeft = self._pipeline.create(dai.node.MonoCamera)
        monoRight = self._pipeline.create(dai.node.MonoCamera)
        stereo = self._pipeline.create(dai.node.StereoDepth)

        # Video saving channels (MJPEG, H264 or H265)
        rgbEncoder = self._pipeline.create(dai.node.VideoEncoder)
        disparityEncoder = self._pipeline.create(dai.node.VideoEncoder)

        # The XlinkOut node sends the video data to the host via XLink (e.g.: Raspi)
        rgbOut = self._pipeline.create(dai.node.XLinkOut)
        disparityOut = self._pipeline.create(dai.node.XLinkOut)

        # Set stream and queue names
        rgbOut.setStreamName("rgb")
        disparityOut.setStreamName("disparity")
        queueNames.append("rgb")
        queueNames.append("disparity")

        # Set resolutions and FPS
        camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
        camRgb.setResolution(self.resolution)
        camRgb.setFps(self.fps)
        
        monoLeft.setResolution(self.monoResolution)
        monoLeft.setCamera("left")
        monoLeft.setFps(self.fps)
        monoRight.setResolution(self.monoResolution)
        monoRight.setCamera("right")
        monoRight.setFps(self.fps)

        # Setting to 26fps will trigger error
        rgbEncoder.setDefaultProfilePreset(25, dai.VideoEncoderProperties.Profile.H265_MAIN)
        # TODO: Not sure if needed
        # disparityEncoder.setDefaultProfilePreset(25, dai.VideoEncoderProperties.Profile.H264_MAIN)
        
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        
        # LR-check is required for depth alignment
        stereo.setLeftRightCheck(True)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)

        # Linking
        camRgb.video.link(rgbOut.input)
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)
        stereo.disparity.link(disparityOut.input)

        camRgb.video.link(rgbEncoder.input)
        # TODO: Not sure if correct
        # disparityOut.out.link(disparityEncoder.input)

        rgbEncoder.bitstream.link(rgbOut.input)
        disparityEncoder.bitstream.link(disparityOut.input)

        # TODO: Check if this is needed in ColorCamera
        #camRgb.setMeshSource(dai.CameraProperties.WarpMeshSource.CALIBRATION)
        if self.alpha is not None:
            camRgb.setCalibrationAlpha(self.alpha)
            stereo.setAlphaScaling(self.alpha)
        
        self._stereo = stereo