from shiny import render, ui


def value(input, output):
    @output
    @render.ui
    def metadata_output():
        elements = []
        if input.id() != "":
            elements.append(ui.markdown(f"ID: {input.id()}"))
        if input.comments() != "":
            elements.append(ui.br())
            elements.append(ui.markdown("Comments:"))
            elements.append(ui.markdown(f"{input.comments()}"))
        return elements
