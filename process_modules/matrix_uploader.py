from process_modules.uploader import BaseUploader
from ui import present


class MatrixUploader(BaseUploader):
    """Uploader for MatrixBuffer - handles visual matrix display with cell highlighting."""

    def __init__(self, disp_out, chrs, buffer_klass):
        super().__init__(disp_out=disp_out, chrs=chrs)
        self.buffer_klass = buffer_klass

    def refresh(self, state="default"):
        """Refresh display based on buffer state."""
        buf = self.buffer_klass.buffer()
        ref_rows = self.buffer_klass.ref_ar()

        for i in range(ref_rows[0], ref_rows[1]):
            if i >= len(buf):
                break
            self._clear_row_display(i)

            row_text = buf[i]
            cursor_row = self.buffer_klass.cursor()
            cursor_col = self.buffer_klass.cursor_col()
            is_editing = self.buffer_klass.is_editing_cell()
            is_save_mode = self.buffer_klass.is_save_mode()

            j_counter = 0
            for j in row_text:
                should_invert = False

                if is_save_mode and i == 6:
                    # Highlight entire "Save matrix" row
                    should_invert = True
                elif is_editing and i == cursor_row and cursor_col >= 0:
                    # Highlight the cell area (5 chars wide)
                    if cursor_col <= j_counter < cursor_col + 5:
                        # Show cursor position within cell
                        cell_cursor = self.buffer_klass.get_cell_cursor_offset()
                        cell_offset = j_counter - cursor_col
                        if cell_offset == cell_cursor:
                            should_invert = True

                self._print_character(j, invert=should_invert)
                j_counter += 1

        self._display_bar(state)
        present()
