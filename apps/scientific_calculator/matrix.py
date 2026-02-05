from mocking import utime as time  # type:ignore
from data_modules.object_handler import display, nav, typer, keypad_state_manager, chrs
from data_modules.object_handler import current_app, data_bucket, menu, menu_refresh
from data_modules.object_handler import form, form_refresh, text, text_refresh, function_buffer
from data_modules.object_handler import popup_menu, popup_refresh
from process_modules.matrix_buffer import MatrixBuffer
from process_modules.matrix_uploader import MatrixUploader


# Global matrix buffer to persist data across screens
matrix_buffer = MatrixBuffer(rows=7, cols=21)
MATRIX_TOOLKIT_ITEMS = [
    "Transpose",
    "Inverse",
]


def matrix_multiply(a, b):
    """Multiply two matrices."""
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])

    if cols_a != rows_b:
        return None  # Cannot multiply

    result = []
    for i in range(rows_a):
        row = []
        for j in range(cols_b):
            val = 0
            for k in range(cols_a):
                val += float(a[i][k]) * float(b[k][j])
            row.append(str(val))
        result.append(row)
    return result


def matrix_add(a, b):
    """Add two matrices."""
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return None
    result = []
    for i in range(len(a)):
        row = []
        for j in range(len(a[0])):
            val = float(a[i][j]) + float(b[i][j])
            row.append(str(val))
        result.append(row)
    return result


def matrix_subtract(a, b):
    """Subtract matrix b from matrix a."""
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return None
    result = []
    for i in range(len(a)):
        row = []
        for j in range(len(a[0])):
            val = float(a[i][j]) - float(b[i][j])
            row.append(str(val))
        result.append(row)
    return result


def matrix_transpose(a):
    """Transpose a matrix."""
    rows, cols = len(a), len(a[0])
    return [[a[r][c] for r in range(rows)] for c in range(cols)]


def matrix_inverse(a):
    """Inverse of a square matrix. Returns None if not invertible."""
    n = len(a)
    if n == 0 or len(a[0]) != n:
        return None

    # Build augmented matrix [A | I]
    aug = []
    for r in range(n):
        row = [float(a[r][c]) for c in range(n)]
        row += [1.0 if r == c else 0.0 for c in range(n)]
        aug.append(row)

    # Gauss-Jordan elimination with partial pivoting
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            return None
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]

        pivot_val = aug[col][col]
        for c in range(2 * n):
            aug[col][c] /= pivot_val

        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor != 0:
                for c in range(2 * n):
                    aug[r][c] -= factor * aug[col][c]

    inv = []
    for r in range(n):
        inv.append([str(aug[r][c + n]) for c in range(n)])
    return inv


def copy_matrix(a):
    """Create a deep copy of a matrix."""
    return [[cell for cell in row] for row in a]


def resolve_matrix_token(token, matrices):
    """Resolve a token to a matrix (supports TR() and INV())."""
    if token in matrices:
        return copy_matrix(matrices[token]), None
    if token.startswith("TR(") and token.endswith(")"):
        inner = token[3:-1].strip()
        if inner in matrices:
            return matrix_transpose(matrices[inner]), None
        return None, "Matrix not found"
    if token.startswith("INV(") and token.endswith(")"):
        inner = token[4:-1].strip()
        if inner in matrices:
            inv = matrix_inverse(matrices[inner])
            if inv is None:
                return None, "Not invertible"
            return inv, None
        return None, "Matrix not found"
    return None, "Invalid expression"


def parse_and_evaluate(expression, matrices):
    """Parse and evaluate matrix expression like 'A + B' or 'A * B - C'."""
    # Simple parser for matrix expressions
    # Supports: +, -, *
    # Returns result matrix or None on error

    expression = expression.strip().upper()
    if not expression:
        return None, "Invalid expression"

    # Tokenize: split by operators while keeping them
    tokens = []
    current = ""
    for char in expression:
        if char in "+-*":
            if current.strip():
                tokens.append(current.strip())
            tokens.append(char)
            current = ""
        elif char != " ":
            current += char
    if current.strip():
        tokens.append(current.strip())

    if not tokens:
        return None, "Invalid expression"

    # First token must resolve to a matrix
    result, err = resolve_matrix_token(tokens[0], matrices)
    if result is None:
        return None, err

    i = 1
    while i < len(tokens):
        if i + 1 >= len(tokens):
            return None, "Invalid expression"  # Incomplete expression

        op = tokens[i]
        operand = tokens[i + 1]

        mat_b, err = resolve_matrix_token(operand, matrices)
        if mat_b is None:
            return None, err

        if op == "+":
            result = matrix_add(result, mat_b)
        elif op == "-":
            result = matrix_subtract(result, mat_b)
        elif op == "*":
            result = matrix_multiply(result, mat_b)
        else:
            return None, "Invalid expression"

        if result is None:
            return None, "Size mismatch"

        i += 2

    return result, None


def _insert_transpose_placeholder():
    token = "Tr( )"
    start = text.menu_buffer_cursor
    raw = text.text_buffer[: text.text_buffer_nospace]
    new_raw = raw[:start] + token + raw[start:]
    text.set_text(new_raw, cursor=start)
    end = start + len(token)
    arg_start = start + 3
    arg_end = start + 4
    function_buffer.set_block("transpose", start, end, arg_start, arg_end)


def _insert_inverse_placeholder():
    token = "Inv( )"
    start = text.menu_buffer_cursor
    raw = text.text_buffer[: text.text_buffer_nospace]
    new_raw = raw[:start] + token + raw[start:]
    text.set_text(new_raw, cursor=start)
    end = start + len(token)
    arg_start = start + 4
    arg_end = start + 5
    function_buffer.set_block("inverse", start, end, arg_start, arg_end)


def _apply_function_argument(arg_text):
    if not function_buffer.active:
        return
    raw = text.text_buffer[: text.text_buffer_nospace]
    start = function_buffer.arg_start
    end = function_buffer.arg_end
    new_raw = raw[:start] + arg_text + raw[end:]
    old_len = function_buffer.block_end - function_buffer.block_start
    old_arg_len = function_buffer.arg_end - function_buffer.arg_start
    new_len = old_len - old_arg_len + len(arg_text)
    new_cursor = function_buffer.block_start + new_len
    text.set_text(new_raw, cursor=new_cursor)
    function_buffer.clear()


def _matrix_argument_write():
    form.input_list = {"inp_0": " "}
    form.form_list = ["Write matrix", "Name:", "inp_0"]
    form.update()
    display.clear_display()
    form_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return None

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return None

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            form.update_buffer("")
        elif inp == "ok":
            name = form.inp_list()["inp_0"].strip().upper()
            if name:
                return name
        else:
            form.update_buffer(inp)

        form_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _matrix_argument_picker():
    menu_items = ["Write"] + matrix_buffer.get_all_matrix_names()
    menu.menu_list = menu_items
    menu.update()
    display.clear_display()
    menu_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            display.clear_display()
            text_refresh.refresh()
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            menu.update_buffer("")
        elif inp == "nav_u" or inp == "nav_d":
            menu.update_buffer(inp)
        elif inp == "ok":
            selected = menu.menu_list[menu.menu_cursor]
            if selected == "Write":
                name = _matrix_argument_write()
                if name:
                    _apply_function_argument(name)
            else:
                _apply_function_argument(selected)
            return

        menu_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _matrix_toolkit(context="default"):
    """Show matrix toolkit menu (text-only placeholders)."""
    menu_items = MATRIX_TOOLKIT_ITEMS + ["Add function"]
    menu.menu_list = menu_items
    menu.update()
    display.clear_display()
    menu_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            menu.update_buffer("")
        elif inp == "nav_u" or inp == "nav_d":
            menu.update_buffer(inp)
        elif inp == "ok":
            selected = menu.menu_list[menu.menu_cursor]
            if context == "calc" and selected == "Transpose":
                _insert_transpose_placeholder()
                return
            if context == "calc" and selected == "Inverse":
                _insert_inverse_placeholder()
                return
            _show_error("Coming soon")
            menu.menu_list = menu_items
            menu.update()
            display.clear_display()
            menu_refresh.refresh()

        menu_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _delete_matrix_popup(matrix_name):
    popup_items = [f"Delete {matrix_name}?", "No", "Yes"]
    popup_menu.menu_list = popup_items
    popup_menu.update()
    display.clear_display()
    popup_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            popup_menu.update_buffer("")
        elif inp == "nav_u" or inp == "nav_d":
            popup_menu.update_buffer(inp)
        elif inp == "ok":
            selected = popup_menu.menu_list[popup_menu.menu_cursor]
            if selected == "Yes":
                if not matrix_buffer.delete_matrix(matrix_name):
                    _show_error("Cannot delete")
                return
            return

        popup_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def matrix(db={}):
    """Main matrix app - shows menu of matrices."""
    global matrix_buffer

    while True:
        # Build main menu list
        menu_items = []
        for name in matrix_buffer.get_all_matrix_names():
            rows, cols = matrix_buffer.get_matrix_size(name)
            menu_items.append(f"{name} {rows}x{cols} OK to edit")
        menu_items.append("Add matrix       OK")
        menu_items.append("Perform calculation")
        menu_items.append("Default (Reset)")

        menu.menu_list = menu_items
        menu.update()
        display.clear_display()
        menu_refresh.refresh()

        while True:
            inp = typer.start_typing()

            if inp == "back":
                current_app[0] = "scientific_calculator"
                current_app[1] = "application_modules"
                return

            if inp == "home":
                current_app[0] = "home"
                current_app[1] = "root"
                return

            if inp == "nav_b":
                selected_idx = menu.menu_cursor
                total_matrices = len(matrix_buffer.get_all_matrix_names())
                if selected_idx < total_matrices:
                    matrix_name = matrix_buffer.get_all_matrix_names()[selected_idx]
                    _delete_matrix_popup(matrix_name)
                    break

            if inp == "toolbox":
                _matrix_toolkit()
                break

            if inp == "alpha" or inp == "beta":
                keypad_state_manager(x=inp)
                menu.update_buffer("")
            elif inp == "nav_u" or inp == "nav_d":
                menu.update_buffer(inp)
            elif inp == "ok":
                selected_idx = menu.menu_cursor
                total_matrices = len(matrix_buffer.get_all_matrix_names())

                if selected_idx < total_matrices:
                    # Selected a matrix - go to dimension form
                    matrix_name = matrix_buffer.get_all_matrix_names()[selected_idx]
                    _dimension_form(matrix_name)
                elif selected_idx == total_matrices:
                    # Add matrix
                    _add_matrix_dialog()
                elif selected_idx == total_matrices + 1:
                    # Perform calculation
                    _calculation_editor()
                elif selected_idx == total_matrices + 2:
                    # Default (Reset)
                    matrix_buffer.reset_all()
                break  # Refresh menu after action

            menu_refresh.refresh(state=nav.current_state())
            time.sleep(0.05)


def _dimension_form(matrix_name):
    """Form to set matrix dimensions, then go to editor."""
    global matrix_buffer

    rows, cols = matrix_buffer.get_matrix_size(matrix_name)

    form.input_list = {"inp_0": str(rows) + " ", "inp_1": str(cols) + " "}
    form.form_list = [f"Matrix {matrix_name}", "Row", "inp_0", "Column", "inp_1", "Build the matrix"]
    form.update()
    display.clear_display()
    form_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "toolbox":
            _matrix_toolkit()
            display.clear_display()
            form_refresh.refresh()
            continue

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            form.update_buffer("")
        elif inp == "ok":
            # Check if on "Build the matrix" option
            if form.menu_cursor == 5:  # Last item index
                try:
                    new_rows = int(form.inp_list()["inp_0"].strip())
                    new_cols = int(form.inp_list()["inp_1"].strip())
                    if new_rows > 0 and new_cols > 0 and new_rows <= 20 and new_cols <= 20:
                        matrix_buffer.resize_matrix(matrix_name, new_rows, new_cols)
                        matrix_buffer.switch_matrix(matrix_name)
                        _matrix_editor(matrix_name)
                        return
                except ValueError:
                    pass
            else:
                form.update_buffer(inp)
        else:
            form.update_buffer(inp)

        form_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _matrix_editor(matrix_name):
    """Visual matrix editor with R/C headers."""
    global matrix_buffer

    matrix_buffer.switch_matrix(matrix_name)
    matrix_uploader = MatrixUploader(
        disp_out=display,
        chrs=chrs,
        buffer_klass=matrix_buffer
    )

    display.clear_display()
    matrix_uploader.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            # Save current cell and exit
            matrix_buffer._save_cell_text()
            return

        if inp == "home":
            matrix_buffer._save_cell_text()
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "toolbox":
            _matrix_toolkit()
            display.clear_display()
            matrix_uploader.refresh()
            continue

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            result = matrix_buffer.update_buffer("")
        else:
            result = matrix_buffer.update_buffer(inp)

        if result == "edit_cell":
            _matrix_cell_full_editor()
            display.clear_display()
            matrix_uploader.refresh()
            continue

        matrix_uploader.refresh(state=nav.current_state())
        time.sleep(0.05)


def _matrix_cell_full_editor():
    value = matrix_buffer.get_cell_text()
    form.input_list = {"inp_0": value + " "}
    form.form_list = ["inp_0"]
    form.update()
    form.input_cursor = len(value)
    form.input_display_position = max(0, len(value) - form.input_cols)
    display.clear_display()
    form_refresh.refresh()

    def _commit_value():
        value = form.inp_list()["inp_0"].strip()
        matrix_buffer.cell_text = value
        matrix_buffer.cell_cursor = len(value)
        matrix_buffer.cell_overwrite = False
        matrix_buffer.cell_overflow = len(value) > 2
        matrix_buffer._save_cell_text()
        matrix_buffer._update_display_buffer()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            _commit_value()
            return

        if inp == "home":
            _commit_value()
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            form.update_buffer("")
        elif inp == "ok":
            _commit_value()
            return
        else:
            form.update_buffer(inp)

        form_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _matrix_cell_viewer_readonly(buffer):
    value = buffer.get_cell_text()
    form.input_list = {"inp_0": value + " "}
    form.form_list = ["inp_0"]
    form.update()
    form.input_cursor = len(value)
    form.input_display_position = max(0, len(value) - form.input_cols)
    display.clear_display()
    form_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            form.update_buffer("")
        elif inp in ["nav_l", "nav_r", "nav_u", "nav_d"]:
            form.update_buffer(inp)

        form_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _add_matrix_dialog():
    """Dialog to add a new matrix."""
    global matrix_buffer

    form.input_list = {"inp_0": " "}
    form.form_list = ["Add New Matrix", "Name (A-Z):", "inp_0"]
    form.update()
    display.clear_display()
    form_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "toolbox":
            _matrix_toolkit()
            display.clear_display()
            form_refresh.refresh()
            continue

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            form.update_buffer("")
        elif inp == "ok":
            name = form.inp_list()["inp_0"].strip().upper()
            if name and len(name) == 1 and name.isalpha():
                if matrix_buffer.add_matrix(name):
                    return
        else:
            form.update_buffer(inp)

        form_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _calculation_editor():
    """Text editor for matrix calculations like 'A + B'."""
    global matrix_buffer

    # Mapping for operator key names to symbols
    key_to_symbol = {
        "plus": "+",
        "minus": "-",
        "multiply": "*",
        "*": "*",
        "/": "/",
        "+": "+",
        "-": "-",
    }

    text.all_clear()
    function_buffer.clear()
    display.clear_display()
    text_refresh.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            function_buffer.clear()
            return

        if inp == "home":
            function_buffer.clear()
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "toolbox":
            _matrix_toolkit(context="calc")
            display.clear_display()
            text_refresh.refresh()
            continue

        if inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            text.update_buffer("")
        elif inp == "ok":
            if function_buffer.is_cursor_in_block(text.menu_buffer_cursor):
                _matrix_argument_picker()
                display.clear_display()
                text_refresh.refresh()
                continue
            # Get expression and evaluate
            expression = text.text_buffer.replace("𖤓", "").strip()
            if expression:
                result, err = parse_and_evaluate(expression, matrix_buffer.matrices)
                if result:
                    _show_result_matrix(result)
                else:
                    _show_error(err or "Invalid expression")
            function_buffer.clear()
            display.clear_display()
            text_refresh.refresh()
            continue
        else:
            # Convert operator key names to symbols
            converted_inp = key_to_symbol.get(inp, inp)
            if function_buffer.active:
                function_buffer.clear()
            text.update_buffer(converted_inp)

        text_refresh.refresh(state=nav.current_state())
        time.sleep(0.05)


def _show_result_matrix(result_matrix):
    """Display result matrix in grid view (read-only)."""
    # Create temporary buffer for result display
    temp_buffer = MatrixBuffer(rows=7, cols=21)
    temp_buffer.set_matrix("Result", result_matrix)
    temp_buffer.switch_matrix("Result")
    temp_buffer.set_result_mode(True)  # Hide "Save matrix" option

    matrix_uploader = MatrixUploader(
        disp_out=display,
        chrs=chrs,
        buffer_klass=temp_buffer
    )

    display.clear_display()
    matrix_uploader.refresh()

    while True:
        inp = typer.start_typing()

        if inp == "back":
            return

        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return

        if inp == "toolbox":
            _matrix_toolkit()
            display.clear_display()
            matrix_uploader.refresh()
            continue

        if inp == "ok":
            _matrix_cell_viewer_readonly(temp_buffer)
            display.clear_display()
            matrix_uploader.refresh()
            continue

        # Allow navigation to view large matrices
        if inp in ["nav_u", "nav_d", "nav_l", "nav_r"]:
            temp_buffer.update_buffer(inp)
            matrix_uploader.refresh(state=nav.current_state())

        time.sleep(0.05)


def _show_error(message):
    """Show error message."""
    menu.menu_list = [message, "", "Press back to return"]
    menu.update()
    display.clear_display()
    menu_refresh.refresh()

    while True:
        inp = typer.start_typing()
        if inp == "back" or inp == "ok":
            return
        if inp == "home":
            current_app[0] = "home"
            current_app[1] = "root"
            return
        time.sleep(0.05)
