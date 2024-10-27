import logging
import os
import time
from datetime import datetime, timedelta

import cv2
import depthai as dai
from depthai_sdk import OakCamera, RecordType

from features.modules.light_barrier import LightBarrier
from features.modules.time_window import TimeWindow
from features.modules.timestamps import Timestamps
from utils.parser import ENVParser


class Camera(object):
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
            cls.fps = 40
        return cls._instance

    def run(self, timestamps: Timestamps, block=False) -> int:
        logging.info("Start process to record with camera.")
        env = ENVParser()
        self.running = True
        state = LightBarrier()

        with OakCamera() as oak:
            # Define cameras
            oak.device.setTimesync(timedelta(seconds=1), 10, True)

            color = oak.camera(
                source=dai.CameraBoardSocket.CAM_A,
                resolution=dai.ColorCameraProperties.SensorResolution.THE_1080_P,
                fps=self.fps,
                encode=self.encode if self.mode else None,
            )
            stereo = oak.stereo(
                resolution=dai.MonoCameraProperties.SensorResolution.THE_800_P,
                fps=self.fps,
                encode=self.encode,
            )

            # Set IR brightness
            # Turned off IR because of the possible marker disruptions
            stereo.set_auto_ir(auto_mode=False, continuous_mode=False)
            stereo.set_ir(0, 0)
            logging.info("Set camera parameters for recording with OAK camera.")

            # Synchronize & save all (encoded) streams
            if self.mode:
                logging.info("Record video without stream.")
                # Folder parameters
                day = datetime.now().strftime(env.date_format)

                oak.record(
                    [color.out.encoded, stereo.out.encoded],
                    os.path.join(env.temp_path, day),
                    RecordType.VIDEO,
                )
            else:
                logging.info("View video without recording.")
                oak.visualize([color.out.camera, stereo.out.depth], fps=True, scale=1 / 2)

            oak.start(blocking=block)
            logging.info(f"Camera started recording at: {datetime.now()}")

            timestamps.camera_start = datetime.now()
            current_state = 0
            startpoint = None
            while oak.running():
                time.sleep(0.001)
                oak.poll()

                if not self.ready:  # not state.activated or
                    oak.device.close()
                    cv2.destroyAllWindows()

                    if startpoint is not None:
                        endpoint = datetime.now()
                        logging.info(f"Light barrier triggered to end at: {endpoint}")
                        if endpoint - startpoint > timedelta(seconds=2):
                            timestamps.time_windows.append(TimeWindow(start=startpoint, end=endpoint))

                try:
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
                except:
                    logging.warning("There was an issue storing a time point.")

            self.running = False

            return 1

    @property
    def camera_connection(self):
        return False if dai.DeviceBootloader.getAllAvailableDevices() == [] else True

    @property
    def ready(self):
        return self._ready

    @ready.setter
    def ready(self, value: bool):
        self._ready = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: bool):
        self._mode = value


if __name__ == "__main__":
    cam = Camera()
    cam.run()
