class SearchBuffer:
    """Buffer class for searchable list with input field on row 0 and results below."""

    def __init__(self, rows=7, cols=21, constants_data=None):
        # Display configuration
        self.rows = rows  # Total rows (0-6, row 7 is status bar)
        self.cols = cols
        self.list_rows = 6  # Rows 1-6 for results

        # Search input state (row 0)
        self.search_text = " "  # Always end with space like Form class
        self.search_cursor = 0
        self.search_display_position = 0
        self.search_cols = cols - 2  # Reserve 2 chars for "=>" prefix

        # Constants data: list of tuples (symbol, name, value)
        self.all_constants = constants_data if constants_data else []

        # Filtered results
        self.filtered_constants = []

        # List navigation state (for results in rows 1-6)
        self.list_cursor = 0  # Which result item is selected (0-based in filtered list)
        self.list_display_position = 0  # First visible item index in filtered list

        # Mode: 'search' (editing search field) or 'list' (browsing results)
        self.mode = 'search'

        # Display buffer for the 7 visible rows
        self.display_buffer = []

        # Refresh tracking
        self.refresh_rows = (0, self.rows)

        # Initialize
        self._filter_constants()
        self._update_display_buffer()

    def update_buffer(self, inp):
        """Handle all input including navigation and character input."""
        result = None

        if inp == "ok":
            if self.mode == 'search':
                # Switch to list mode if there are results
                if self.filtered_constants:
                    self.mode = 'list'
                    self.list_cursor = 0
                    self.list_display_position = 0
                self.refresh_rows = (0, self.rows)
            else:
                # In list mode, OK selects current constant
                result = self._get_selected_constant()
                self.refresh_rows = (0, self.rows)

        elif inp == "nav_u":
            if self.mode == 'list':
                if self.list_cursor > 0:
                    self.list_cursor -= 1
                    if self.list_cursor < self.list_display_position:
                        self.list_display_position -= 1
                        self.refresh_rows = (1, self.rows)
                    else:
                        # Only refresh the two affected rows
                        row_old = self.list_cursor - self.list_display_position + 2
                        row_new = self.list_cursor - self.list_display_position + 1
                        self.refresh_rows = (row_new, row_old + 1)
                else:
                    # At top of list, switch back to search mode
                    self.mode = 'search'
                    self.refresh_rows = (0, self.rows)

        elif inp == "nav_d":
            if self.mode == 'search':
                # Switch to list mode
                if self.filtered_constants:
                    self.mode = 'list'
                    self.list_cursor = 0
                    self.list_display_position = 0
                self.refresh_rows = (0, self.rows)
            elif self.mode == 'list':
                if self.list_cursor < len(self.filtered_constants) - 1:
                    self.list_cursor += 1
                    if self.list_cursor >= self.list_display_position + self.list_rows:
                        self.list_display_position += 1
                        self.refresh_rows = (1, self.rows)
                    else:
                        # Only refresh the two affected rows
                        row_old = self.list_cursor - self.list_display_position
                        row_new = self.list_cursor - self.list_display_position + 1
                        self.refresh_rows = (row_old, row_new + 1)

        elif inp == "nav_l":
            if self.mode == 'search':
                self.search_cursor -= 1
                if self.search_cursor < 0:
                    self.search_cursor = len(self.search_text) - 1
                    self.search_display_position = max(0, len(self.search_text) - self.search_cols)
                elif self.search_cursor < self.search_display_position:
                    self.search_display_position -= 1
                self.refresh_rows = (0, 1)

        elif inp == "nav_r":
            if self.mode == 'search':
                self.search_cursor += 1
                if self.search_cursor >= len(self.search_text):
                    self.search_cursor = 0
                    self.search_display_position = 0
                elif self.search_cursor >= self.search_display_position + self.search_cols:
                    self.search_display_position += 1
                self.refresh_rows = (0, 1)

        elif inp == "nav_b":
            if self.mode == 'search':
                # Backspace: move cursor left and delete character
                self.search_cursor -= 1
                if self.search_cursor < 0:
                    self.search_cursor = len(self.search_text) - 1
                    self.search_display_position = max(0, len(self.search_text) - self.search_cols)
                elif self.search_cursor < self.search_display_position:
                    self.search_display_position -= 1

                # Delete character at cursor if not at end
                if self.search_cursor < len(self.search_text) - 1:
                    self.search_text = self.search_text[:self.search_cursor] + self.search_text[self.search_cursor + 1:]
                    # Adjust display position if needed
                    if len(self.search_text) > self.search_cols and len(self.search_text[self.search_display_position:]) < self.search_cols:
                        self.search_display_position = len(self.search_text) - self.search_cols
                    elif len(self.search_text) <= self.search_cols:
                        self.search_display_position = 0

                self._filter_constants()
                self.refresh_rows = (0, self.rows)

        elif inp == "AC":
            # Clear search text
            self.search_text = " "
            self.search_cursor = 0
            self.search_display_position = 0
            self.mode = 'search'
            self._filter_constants()
            self.refresh_rows = (0, self.rows)

        else:
            # Character input in search mode
            if self.mode == 'search' and inp and len(inp) >= 1:
                for char in inp:
                    self.search_text = self.search_text[:self.search_cursor] + char + self.search_text[self.search_cursor:]
                    self.search_cursor += 1
                    if self.search_cursor >= self.search_display_position + self.search_cols:
                        self.search_display_position += 1
                # Ensure trailing space
                self.search_text = self.search_text.rstrip() + " "
                self._filter_constants()
                # Reset list position when filter changes
                self.list_cursor = 0
                self.list_display_position = 0
                self.refresh_rows = (0, self.rows)

        self._update_display_buffer()
        return result

    def _filter_constants(self):
        """Filter constants based on search_text (case-insensitive partial match)."""
        query = self.search_text.strip().lower()
        if not query:
            self.filtered_constants = self.all_constants[:]
        else:
            self.filtered_constants = [
                c for c in self.all_constants
                if query in c[0].lower() or query in c[1].lower()
            ]
        # Reset list position when filter changes
        self.list_cursor = 0
        self.list_display_position = 0

    def _update_display_buffer(self):
        """Build the 7-row display buffer."""
        self.display_buffer = []

        # Row 0: Search input with "=>" prefix
        search_visible = self.search_text[self.search_display_position:self.search_display_position + self.search_cols]
        search_display = "=>" + search_visible
        if len(search_display) < self.cols:
            search_display += " " * (self.cols - len(search_display))
        self.display_buffer.append(search_display)

        # Rows 1-6: Filtered results
        for i in range(self.list_rows):
            idx = self.list_display_position + i
            if idx < len(self.filtered_constants):
                symbol, name, value = self.filtered_constants[idx]
                # Format: "symbol: value" (truncated to fit)
                display_text = f"{symbol}: {value}"
                if len(display_text) > self.cols:
                    display_text = display_text[:self.cols - 2] + ".."
                display_text = display_text.ljust(self.cols)
            else:
                display_text = " " * self.cols
            self.display_buffer.append(display_text)

    def _get_selected_constant(self):
        """Return the currently selected constant tuple or None."""
        if self.filtered_constants and 0 <= self.list_cursor < len(self.filtered_constants):
            return self.filtered_constants[self.list_cursor]
        return None

    def buffer(self):
        """Return display buffer."""
        return self.display_buffer

    def cursor(self):
        """Return display cursor row position."""
        if self.mode == 'search':
            return 0
        else:
            return self.list_cursor - self.list_display_position + 1  # +1 because row 0 is search

    def ref_ar(self):
        """Return refresh rows tuple."""
        return self.refresh_rows

    def is_search_mode(self):
        """Return True if in search mode."""
        return self.mode == 'search'

    def search_cursor_position(self):
        """Return cursor position within search row for highlighting."""
        return self.search_cursor - self.search_display_position + 2  # +2 for "=>" prefix

    def get_search_text(self):
        """Return current search text."""
        return self.search_text

    def update(self):
        """Reset buffer state."""
        self.search_text = " "
        self.search_cursor = 0
        self.search_display_position = 0
        self.list_cursor = 0
        self.list_display_position = 0
        self.mode = 'search'
        self._filter_constants()
        self._update_display_buffer()
        self.refresh_rows = (0, self.rows)
