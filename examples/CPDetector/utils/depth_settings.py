import depthai as dai

class DepthSettings:
    def __init__(self, pipeline: dai.Pipeline, fps: int) -> None:
        # Camera parameters
        self.fps = fps
        #self.alpha = cmd_parser.alpha
        self.resolution = dai.MonoCameraProperties.SensorResolution.THE_800_P # Resolution is set as close as possible to Yolov8 input size (YOLOv8x-pose-p6: size=1280)

        # Pipeline Parameters
        self._pipeline = pipeline
        self._stereo = None

    @property
    def pipeline(self):
        return self._pipeline
    
    @property
    def stereo(self):
        return self._stereo

    def setup_pipeline(self):
        ## Define sources and outputs
        # Displaying channels
        monoLeft = self._pipeline.create(dai.node.MonoCamera)
        monoRight = self._pipeline.create(dai.node.MonoCamera)
        stereo = self._pipeline.create(dai.node.StereoDepth)

        # Video saving channels (MJPEG, H264 or H265)
        disparityEncoder = self._pipeline.create(dai.node.VideoEncoder)

        # The XlinkOut node sends the video data to the host via XLink (e.g.: Raspi)
        disparityOut = self._pipeline.create(dai.node.XLinkOut)

        # Set stream and queue names
        disparityOut.setStreamName("disparity")
        
        # Set resolutions and FPS and select cameras
        monoLeft.setResolution(self.resolution)
        monoLeft.setCamera("left")
        monoLeft.setFps(self.fps)
        monoRight.setResolution(self.resolution)
        monoRight.setCamera("right")
        monoRight.setFps(self.fps)

        # Setting to 26fps will trigger error
        disparityEncoder.setDefaultProfilePreset(self.fps, dai.VideoEncoderProperties.Profile.H264_MAIN)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        
        # LR-check is required for depth alignment
        stereo.setLeftRightCheck(True)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)

        # Linking
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)
        stereo.disparity.link(disparityOut.input)
        disparityEncoder.bitstream.link(disparityOut.input)

        # AlphaScaling is used after undistortion of image
        #if self.alpha is not None:
        #    stereo.setAlphaScaling(self.alpha)
       # 
        self._stereo = stereo