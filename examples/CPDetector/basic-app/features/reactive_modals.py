from shiny import reactive, ui


def values(input):
    @reactive.Effect
    @reactive.event(input.delete_yes, input.delete_no)
    def modal_remover():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.save_yes, input.save_no)
    def modal_remover_2():
        ui.modal_remove()
