"""
This module provides functionality to manage and operate the camera for recording sessions.

It defines the Camera class which handles the initialization, running, and state management of the camera.

Classes:
    Camera: Manages the camera operations including recording and state management.

Methods:
    run: Starts the camera recording process.
"""

import logging
import os
from datetime import datetime, timedelta

import cv2
import depthai as dai
import numpy as np

from features.modules.light_barrier import LightBarrier
from features.modules.time_window import TimeWindow
from features.modules.timestamps import Timestamps
from utils.parser import ENVParser


class Camera(object):
    """
    Manages the camera operations including recording and state management.

    Attributes:
        _instance (Camera): Singleton instance of the Camera class.
        running (bool): Indicates if the camera is currently running.
        encode (dai.VideoEncoderProperties.Profile): The encoding profile for the video.
        fps (int): Frames per second for the camera.
        _ready (bool): Indicates if the camera is ready.
        _mode (bool): Indicates the mode of the camera (recording or viewing).
    """

    _instance = None
    running = False
    encode = None
    fps = None
    _ready = False
    _mode = False

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate camera instance.")
            cls._instance = super(Camera, cls).__new__(cls)
            cls.encode = dai.VideoEncoderProperties.Profile.H265_MAIN
            cls.fps = 30
        return cls._instance

    def run(self, timestamps: Timestamps, block=False) -> int:
        """
        Starts the camera recording process.

        Args:
            timestamps (Timestamps): The timestamps object to store recording times.
            block (bool): Whether to block the execution until recording is finished. Defaults to False.

        Returns:
            int: Status code indicating the result of the operation.
        """
        logging.info("Start process to record with camera.")
        env = ENVParser()
        self.running = True
        state = LightBarrier()

        # Create Pipeline
        pipeline = dai.Pipeline()

        # Define sources and outputs
        color = pipeline.create(dai.node.ColorCamera)
        color.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        color.setFps(self.fps)
        color.setCamera("color")

        monoLeft = pipeline.create(dai.node.MonoCamera)
        monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_800_P)
        monoLeft.setFps(self.fps)
        monoLeft.setCamera("left")

        monoRight = pipeline.create(dai.node.MonoCamera)
        monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_800_P)
        monoRight.setFps(self.fps)
        monoRight.setCamera("right")

        stereo = pipeline.create(dai.node.StereoDepth)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)
        #stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        stereo.setLeftRightCheck(True)
        stereo.setExtendedDisparity(False)  # This needs to be set to False. Otherwise the number of frames differ for depth and color
        stereo.setSubpixel(False)

        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)

        if self.mode:  # Recording mode
            # Video encoder node
            video_encoder_color = pipeline.create(dai.node.VideoEncoder)
            video_encoder_color.setDefaultProfilePreset(self.fps, self.encode)
            color.video.link(video_encoder_color.input)

            # Color output node
            xout_video = pipeline.create(dai.node.XLinkOut)
            xout_video.setStreamName("video")
            video_encoder_color.bitstream.link(xout_video.input)

            # Depth output node
            video_encoder_depth = pipeline.create(dai.node.VideoEncoder)
            video_encoder_depth.setDefaultProfilePreset(self.fps, self.encode)
            stereo.disparity.link(video_encoder_depth.input)

            xout_depth = pipeline.create(dai.node.XLinkOut)
            xout_depth.setStreamName("disparity")
            video_encoder_depth.bitstream.link(xout_depth.input)

            logging.info("Record video without stream.")


        else:  # Viewing mode
            color.setIspScale(1, 2)

            xoutGrp = pipeline.create(dai.node.XLinkOut)
            xoutGrp.setStreamName("xout")

            # Sync outputs with each other
            sync = pipeline.create(dai.node.Sync)
            sync.setSyncThreshold(timedelta(milliseconds=50))
            stereo.disparity.link(sync.inputs["disparity"])
            color.video.link(sync.inputs["video"])
            sync.out.link(xoutGrp.input)

            logging.info("View video without recording.")

             
        with dai.Device(pipeline) as device:
            logging.info(f"Camera started recording at: {datetime.now()}")
            timestamps.camera_start = datetime.now()
            current_state = 0
            startpoint = None
            device.setIrLaserDotProjectorIntensity(0)
            device.setIrFloodLightIntensity(0)
            logging.info("Set camera parameters for recording with OAK camera.")
            device.readCalibration().setFov(dai.CameraBoardSocket.CAM_B, 127)
            device.readCalibration().setFov(dai.CameraBoardSocket.CAM_C, 127)

            if self.mode:  # Recording mode
                disparity_queue = device.getOutputQueue(name="disparity", maxSize=50, blocking=block)
                video_queue = device.getOutputQueue(name="video", maxSize=50, blocking=block)
                color_frame = None
                disparity_frame = None

                # Open a file to save encoded video
                day = datetime.now().strftime(env.date_format)
                os.makedirs(os.path.join(env.temp_path, day), exist_ok=True)
                with open(os.path.join(env.temp_path, day, "color.mp4"), 'wb') as video_file, open(
                        os.path.join(env.temp_path, day, "disparity.mp4"), 'wb') as depth_file:
                    print("Recording started...")
                    while True:
                        try:
                            while disparity_queue.has():
                                disparity_queue.get().getData().tofile(depth_file)
                            while video_queue.has():
                                video_queue.get().getData().tofile(video_file)

                            if not self.ready:
                                if startpoint is not None:
                                    endpoint = datetime.now()
                                    logging.info(f"Light barrier triggered to end at: {endpoint}")
                                    if endpoint - startpoint > timedelta(seconds=2):
                                        timestamps.time_windows.append(TimeWindow(start=startpoint, end=endpoint))
                                break

                            if current_state != state.activated:
                                if state.activated:
                                    startpoint = datetime.now()
                                    logging.info(f"Light barrier triggered to start at: {startpoint}")
                                else:
                                    endpoint = datetime.now()
                                    logging.info(f"Light barrier triggered to end at: {endpoint}")
                                    if endpoint - startpoint > timedelta(seconds=2):
                                        timestamps.time_windows.append(TimeWindow(start=startpoint, end=endpoint))
                                    startpoint = None
                                    endpoint = None
                            current_state = state.activated


                            """while disparity_queue.has():
                                disparity_frame = disparity_queue.get().getData()
                            while video_queue.has():
                                color_frame = video_queue.get().getData()

                            # Blend when both received
                            if disparity_frame is not None and color_frame is not None:
                                disparity_frame.tofile(depth_file)
                                color_frame.tofile(video_file)"""

                        except:
                            logging.warning("There was an issue storing a time point.")
                            break

            else:  # Viewing mode
                disparityMultiplier = 255.0 / stereo.initialConfig.getMaxDisparity()
                queue = device.getOutputQueue(name="xout", maxSize=30, blocking=block)
                while True:
                    msgGrp = queue.get()
                    for name, msg in msgGrp:
                        frame = msg.getCvFrame()
                        if name == "disparity":
                            frame = (frame * disparityMultiplier).astype(np.uint8)
                            frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
                        cv2.imshow(name, frame)
                    if cv2.waitKey(1) == ord("q") or not self.ready:
                        cv2.destroyAllWindows()
                        break

            self.running = False

            return 1


    @property
    def camera_connection(self) -> bool:
        """
        Checks if the camera is connected.

        Returns:
            bool: True if the camera is connected, False otherwise.
        """
        return False if dai.DeviceBootloader.getAllAvailableDevices() == [] else True

    @property
    def ready(self) -> bool:
        return self._ready

    @ready.setter
    def ready(self, value: bool):
        """
        Sets and Gets the readiness state of the camera.

        Args:
            value (bool): The readiness state to set.
        """
        self._ready = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: bool):
        """
        Sets and Gets the mode of the camera.

        Args:
            value (bool): The mode to set (True for recording, False for viewing).
        """
        self._mode = value


if __name__ == "__main__":
    cam = Camera()
    cam.ready = True
    cam.mode = True
    cam.run(timestamps=Timestamps())
