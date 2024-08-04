from depthai_sdk import OakCamera, RecordType
import depthai as dai
import datetime
import os

from features.modules.light_barrier import LightBarrier

from dotenv import load_dotenv

load_dotenv(
    "/home/pi/Desktop/luxonis/depthai-python/examples/CPDetector/basic-app/.env"
)

temp_path = os.getenv("TEMP_STORAGE")
main_path = os.getenv("MAIN_STORAGE")
date_format = os.getenv("DATE_FORMAT")


class Camera(object):
    _instance = None
    oak = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating the camera object")
            cls._instance = super(Camera, cls).__new__(cls)
            cls.oak = OakCamera()
            # Put any initialization here.
        return cls._instance

    def run(self) -> int:
        state = LightBarrier()
        print("Light Setup")
        with self.oak as oak:

            # Parameters
            encode = dai.VideoEncoderProperties.Profile.H265_MAIN
            resolution = "3040p"
            fps = 60

            # Folder parameters
            day = datetime.datetime.now().strftime(date_format)
            # NOTE: Are more parameters needed?

            # Define cameras
            color = oak.camera(
                source=dai.CameraBoardSocket.CAM_A,
                resolution=resolution,
                fps=fps,
                encode=encode,
            )
            stereo = oak.stereo(resolution=resolution, fps=fps, encode=encode)

            # Set IR brightness
            stereo.set_auto_ir(auto_mode=True, continuous_mode=True)
            # stereo.set_ir(dot_projector_brightness, flood_brightness)

            # Synchronize & save all (encoded) streams
            oak.record(
                [color.out.encoded],
                os.path.join(temp_path, day),
                RecordType.VIDEO,
            )  # TODO: Add: , stereo.out.encoded....back into the list to store the depth
            oak.visualize([color.out.camera], fps=True, scale=1 / 2)
            # oak.show_graph()

            oak.start(blocking=False)
            while oak.running():
                oak.poll()
                if not state.activated:
                    oak.close()

            return 1

    def stop(self):
        self.oak.close()

    @property
    def camera_connection(self):
        return False if dai.DeviceBootloader.getAllAvailableDevices() == [] else True


if __name__ == "__main__":
    cam = Camera()
    cam.run()
