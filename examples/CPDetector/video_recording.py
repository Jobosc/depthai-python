#!/usr/bin/env python3

from depthai_sdk import OakCamera, RecordType
import depthai as dai
import datetime

def set_ir_parameters(stereo: OakCamera.stereo, dot_projector_brightness, flood_brightness):
    stereo.set_ir(dot_projector_brightness, flood_brightness)

def run():
    with OakCamera() as oak:
        # Parameters
        encode = dai.VideoEncoderProperties.Profile.H265_MAIN
        resolution = "800p"
        fps = 60
        dot_projector_brightness = 200
        flood_brightness = 100

        # Folder parameters
        day = datetime.datetime.now().strftime("%Y%m%d")
        # NOTE: Are more parameters needed?

        # Define cameras
        color = oak.camera(source=dai.CameraBoardSocket.CAM_A, resolution=resolution, fps=fps, encode=encode, name="color")
        stereo = oak.stereo(resolution=resolution, fps=fps, encode=encode, name="stereo")
        
        # Set IR brightness
        #stereo.set_auto_ir(auto_mode=True, continuous_mode=True)
        stereo.set_ir(dot_projector_brightness, flood_brightness)
        
        # Synchronize & save all (encoded) streams
        oak.record([color.out.encoded, stereo.out.encoded], f"./VideoRecordings/{day}/", RecordType.VIDEO)
        oak.visualize([color.out.camera, stereo.out.depth], fps=True, scale=1/2)
        oak.start(blocking=False)   # This needs to be unblocked to run the below code. Check if I actually need it.

        # Debug mode
        while oak.running():
            key = oak.poll()
            if key == ord('w'):
                dot_projector_brightness = dot_projector_brightness + 100 if dot_projector_brightness + 100 <= 800 else 800
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)
            elif key == ord('s'):
                dot_projector_brightness = dot_projector_brightness - 100 if dot_projector_brightness - 100 >= 0 else 0
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)
            elif key == ord('a'):
                flood_brightness = flood_brightness + 100 if flood_brightness + 100 <= 800 else 800
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)
            elif key == ord('d'):
                flood_brightness = flood_brightness - 100 if flood_brightness - 100 <= 0 else 0
                set_ir_parameters(stereo, dot_projector_brightness, flood_brightness)

            elif key == ord('e'): # Switch to auto exposure
                stereo.set_auto_ir(auto_mode=True, continuous_mode=True)


if __name__ == "__main__":
    run()