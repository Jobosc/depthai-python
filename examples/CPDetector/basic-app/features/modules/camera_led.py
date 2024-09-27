import faicons as fa
from shiny import reactive
from shiny import render
from ..functions import get_connection_states
from ..reactive_values import camera_state

STATUS = {
    "available": fa.icon_svg(name="circle", fill="green"),
    "missing": fa.icon_svg(name="circle", fill="red"),
    "recording": fa.icon_svg(name="circle", fill="deepskyblue"),
}

camera_led = reactive.Value(STATUS["available"])

def values(camera):
    @render.ui
    def camera_led_update():
        reactive.invalidate_later(0.01)
        connections = get_connection_states()

        camera_state.set(connections)

        if camera.running:
            status = STATUS["recording"]
        elif connections:
            status = STATUS["available"]
        else:
            status = STATUS["missing"]

        return status
    
    #return camera_led_update()
