import datetime
import os

import depthai as dai
from depthai_sdk import OakCamera, RecordType
from dotenv import load_dotenv
from shiny.express import ui

load_dotenv("./.env")

source_path = os.getenv("TEMP_STORAGE")
date_format = os.getenv("DATE_FORMAT")


def set_ir_parameters(
        stereo: OakCamera.stereo, dot_projector_brightness, flood_brightness
):
    stereo.set_ir(dot_projector_brightness, flood_brightness)


@ui.bind_task_button(button_id="record_button")
def run() -> int:
    with OakCamera() as oak:
        # Parameters
        encode = dai.VideoEncoderProperties.Profile.H265_MAIN
        resolution = "800p"
        fps = 60
        dot_projector_brightness = 200
        flood_brightness = 100

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
            os.path.join(source_path, day),
            RecordType.VIDEO,
        )  # TODO: Add: , stereo.out.encoded....back into the list to store the depth
        oak.visualize([color.out.camera, stereo.out.depth], fps=True, scale=1 / 2)
        # oak.show_graph()

        oak.start(
            blocking=False
        )  # This needs to be unblocked to run the below code. Check if I actually need it.
        # oak.close()
        # Debug mode
        while oak.running():
            key = oak.poll()
            if key == ord("w"):
                dot_projector_brightness = (
                    dot_projector_brightness + 100
                    if dot_projector_brightness + 100 <= 800
                    else 800
                )
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)
            elif key == ord("s"):
                dot_projector_brightness = (
                    dot_projector_brightness - 100
                    if dot_projector_brightness - 100 >= 0
                    else 0
                )
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)
            elif key == ord("a"):
                flood_brightness = (
                    flood_brightness + 100 if flood_brightness + 100 <= 800 else 800
                )
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)
            elif key == ord("d"):
                flood_brightness = (
                    flood_brightness - 100 if flood_brightness - 100 <= 0 else 0
                )
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)

            elif key == ord("e"):  # Switch to auto exposure
                stereo.set_auto_ir(auto_mode=True, continuous_mode=True)

        return 1


if __name__ == "__main__":
    run()
