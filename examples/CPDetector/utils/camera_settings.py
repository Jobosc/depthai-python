import depthai as dai
from utils.parser import ENVParser, CMDParser
import os


class CameraSettings:
    def __init__(self):
        env_parser = ENVParser()
        cmd_parser = CMDParser()

        # Weights to use when blending depth/rgb image (should equal 1.0)
        self.rgbWeight = env_parser.rgb_weight

        # Camera parameters
        self.fps = env_parser.fps
        self.alpha = cmd_parser.alpha
        self.resolution = dai.ColorCameraProperties.SensorResolution.THE_800_P # Resolution is set as close as possible to Yolov8 input size (YOLOv8x-pose-p6: size=1280)

        # The disparity is computed at this resolution, then upscaled to RGB resolution
        self.monoResolution = dai.MonoCameraProperties.SensorResolution.THE_800_P

        # Pipeline Parameters
        self._pipeline = dai.Pipeline()
        self._stereo = None

        # Scripts
        self._scripts_folder = f"{os.getcwd()}/examples/CPDetector/scripts"
    
    @property
    def pipeline(self):
        return self._pipeline
    
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

        # Script node
        script = self._pipeline.create(dai.node.Script)
        script.setScriptPath(f"{self._scripts_folder}/forward_frames.py")
        
        camRgb.still.link(script.inputs['frames'])

        # The XlinkOut node sends the video data to the host via XLink (e.g.: Raspi)
        rgbOut = self._pipeline.create(dai.node.XLinkOut)
        rgbOutEncode = self._pipeline.create(dai.node.XLinkOut)
        disparityOut = self._pipeline.create(dai.node.XLinkOut)

        # Set stream and queue names
        rgbOut.setStreamName("rgb")
        rgbOutEncode.setStreamName("rgbEncode")
        disparityOut.setStreamName("disparity")
        queueNames.append("disparity")
        
        # Set resolutions and FPS and select cameras
        camRgb.setResolution(self.resolution)
        camRgb.setFps(self.fps)
        monoLeft.setResolution(self.monoResolution)
        monoLeft.setCamera("left")
        monoLeft.setFps(self.fps)
        monoRight.setResolution(self.monoResolution)
        monoRight.setCamera("right")
        monoRight.setFps(self.fps)

        # Setting to 26fps will trigger error
        rgbEncoder.setDefaultProfilePreset(self.fps, dai.VideoEncoderProperties.Profile.H265_MAIN)
        disparityEncoder.setDefaultProfilePreset(self.fps, dai.VideoEncoderProperties.Profile.H264_MAIN)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        
        # LR-check is required for depth alignment
        stereo.setLeftRightCheck(True)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)

        # Linking
        script.outputs['rgb'].link(rgbOut.input)
        script.outputs['rgbEncode'].link(rgbOutEncode.input)
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)
        stereo.disparity.link(disparityOut.input)

        script.outputs['ctrl'].link(camRgb.inputControl)

        rgbEncoder.bitstream.link(rgbOutEncode.input)
        disparityEncoder.bitstream.link(disparityOut.input)

        # TODO: After purchase of the OAK-D W I need to check if I need to unwarp
        #camRgb.setMeshSource(dai.CameraProperties.WarpMeshSource.CALIBRATION)
        
        # AlphaScaling is used after undistortion of image
        if self.alpha is not None:
            #camRgb.setCalibrationAlpha(self.alpha)
            stereo.setAlphaScaling(self.alpha)
        
        self._stereo = stereo