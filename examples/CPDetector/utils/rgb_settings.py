import depthai as dai
import os

class RGBSettings:
    def __init__(self, pipeline: dai.Pipeline, fps: int) -> None:
        self._pipeline = pipeline
        self._script = f"{os.getcwd()}/examples/CPDetector/scripts/forward_frames.py"
        self._resolution = dai.ColorCameraProperties.SensorResolution.THE_800_P # Resolution is set as close as possible to Yolov8 input size (YOLOv8x-pose-p6: size=1280)
        self._fps = fps
    
    @property
    def pipeline(self):
        return self._pipeline

    def setup_pipeline(self):
        ## Define sources and outputs
        # Sources
        camRgb = self._pipeline.create(dai.node.ColorCamera)    # Display video
        rgbEncoder = self._pipeline.create(dai.node.VideoEncoder)   # Encode video (MJPEG, H264 or H265)
        # Outputs (The XlinkOut node sends the video data to the host via XLink (e.g.: Raspi))
        rgbOut = self._pipeline.create(dai.node.XLinkOut)
        rgbOutEncode = self._pipeline.create(dai.node.XLinkOut)

        # Script node
        script = self._pipeline.create(dai.node.Script)
        script.setScriptPath(self._script)
        camRgb.still.link(script.inputs['frames'])
        
        # Set stream/queue names
        rgbOut.setStreamName("rgb")
        rgbOutEncode.setStreamName("rgbEncode")
        
        # Set Properties (e.g.: resolution, FPS,...)
        camRgb.setIspScale(1,2)     # Sets the image to half the size
        camRgb.setResolution(self._resolution)      # TODO: this could be messing with my output
        camRgb.setFps(self._fps)                    # TODO: this could be messing with my output
        camRgb.setInterleaved(False)                # TODO: this could be messing with my output
        camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)  # TODO: this could be messing with my output

        rgbEncoder.setDefaultProfilePreset(self._fps, dai.VideoEncoderProperties.Profile.H265_MAIN)

        # Linking
        script.outputs['rgb'].link(rgbOut.input)
        script.outputs['rgbEncode'].link(rgbOutEncode.input)
        script.outputs['ctrl'].link(camRgb.inputControl)
        rgbEncoder.bitstream.link(rgbOutEncode.input)

        # TODO: After purchase of the OAK-D W I need to check if I need to unwarp
        #camRgb.setMeshSource(dai.CameraProperties.WarpMeshSource.CALIBRATION)
        
        # AlphaScaling is used after undistortion of image
        #if self.alpha is not None:
            #camRgb.setCalibrationAlpha(self.alpha)