from process_modules.uploader import BaseUploader
from ui import present


class SearchUploader(BaseUploader):
    """Uploader for SearchBuffer - handles search input row and results list."""

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
            j_counter = 0

            for j in row_text:
                should_invert = False

                if i == 0:
                    # Row 0 is search input
                    if self.buffer_klass.is_search_mode():
                        # Highlight character at cursor position
                        if j_counter == self.buffer_klass.search_cursor_position():
                            should_invert = True
                    # When not in search mode, no highlight on search row
                else:
                    # Rows 1-6 are results
                    if not self.buffer_klass.is_search_mode():
                        # In list mode, highlight the entire selected row
                        if i == self.buffer_klass.cursor():
                            should_invert = True

                self._print_character(j, invert=should_invert)
                j_counter += 1

        self._display_bar(state)
        present()
