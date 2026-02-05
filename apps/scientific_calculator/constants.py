from mocking import utime as time  # type:ignore
from data_modules.object_handler import display, nav, typer, keypad_state_manager, chrs
from data_modules.object_handler import current_app, data_bucket
from process_modules.search_buffer import SearchBuffer
from process_modules.search_buffer_uploader import SearchUploader
from apps.scientific_calculator.constants_data import SCIENTIFIC_CONSTANTS


def constants(db={}):
    # Initialize search buffer with all constants
    search_buffer = SearchBuffer(
        rows=7,
        cols=21,
        constants_data=SCIENTIFIC_CONSTANTS
    )

    # Initialize uploader
    search_uploader = SearchUploader(
        disp_out=display,
        chrs=chrs,
        buffer_klass=search_buffer
    )

    display.clear_display()
    search_uploader.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            current_app[0] = "scientific_calculator"
            current_app[1] = "application_modules"
            break

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            search_buffer.update_buffer("")

        elif inp == "ok":
            result = search_buffer.update_buffer(inp)
            if result is not None:
                # User selected a constant - copy value to clipboard
                selected_symbol, selected_name, selected_value = result
                data_bucket["clipboard"] = selected_value
                data_bucket["clipboard_symbol"] = selected_symbol
                # Return to scientific_calculator menu
                current_app[0] = "scientific_calculator"
                current_app[1] = "application_modules"
                break

        elif inp not in ["alpha", "beta"]:
            search_buffer.update_buffer(inp)

        search_uploader.refresh(state=nav.current_state())
        time.sleep(0.1)
