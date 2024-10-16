from shiny import reactive, ui


def update(input):
    @reactive.Effect
    @reactive.event(input.delete_yes, input.delete_no)
    def modal_remover():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.save_yes, input.save_no)
    def modal_remover_2():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.convert_yes, input.convert_no)
    def modal_remover_3():
        ui.modal_remove()
    
    @reactive.Effect
    @reactive.event(input.delete_session_yes, input.delete_session_no)
    def modal_remover_4():
        ui.modal_remove()
    
    @reactive.Effect
    @reactive.event(input.delete_current_session_yes, input.delete_current_session_no)
    def modal_remover_5():
        ui.modal_remove()