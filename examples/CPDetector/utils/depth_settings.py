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

        # Closer-in minimum depth, disparity range is doubled (from 95 to 190):
        self._extended_disparity = False
        # Better accuracy for longer distance, fractional disparity 32-levels:
        self._subpixel = False
        # Better handling for occlusions:
        self._lr_check = True

    @property
    def pipeline(self):
        return self._pipeline
    
    @property
    def stereo(self):
        return self._stereo

    def setup_pipeline(self, save_data: bool):
        # Define sources and outputs
        ## Sources
        monoLeft = self._pipeline.create(dai.node.MonoCamera)
        monoRight = self._pipeline.create(dai.node.MonoCamera)
        stereo = self._pipeline.create(dai.node.StereoDepth) # Displaying channel
        disparityEncoder = self._pipeline.create(dai.node.VideoEncoder) # Encoding channel (MJPEG, H264 or H265)
        # Outputs (The XlinkOut node sends the video data to the host via XLink (e.g.: Raspi))
        disparityOut = self._pipeline.create(dai.node.XLinkOut)
        
        # Set stream/queue names
        disparityOut.setStreamName("disparity")
        
        # Set Properties (e.g.: resolution, FPS,...)
        monoLeft.setResolution(self.resolution)
        monoLeft.setCamera("left")
        monoLeft.setFps(self.fps)
        monoRight.setResolution(self.resolution)
        monoRight.setCamera("right")
        monoRight.setFps(self.fps)

        # Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
        stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        stereo.setLeftRightCheck(self._lr_check)
        stereo.setExtendedDisparity(self._extended_disparity)
        stereo.setSubpixel(self._subpixel)

        disparityEncoder.setDefaultProfilePreset(self.fps, dai.VideoEncoderProperties.Profile.H264_MAIN)

        # Linking
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)

        if save_data:
            stereo.disparity.link(disparityEncoder.input)
            disparityEncoder.bitstream.link(disparityOut.input)
        else:
            stereo.disparity.link(disparityOut.input)
        
        # AlphaScaling is used after undistortion of image
        #if self.alpha is not None:
        #    stereo.setAlphaScaling(self.alpha)
        
        self._stereo = stereo