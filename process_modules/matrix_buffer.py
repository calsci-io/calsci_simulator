class MatrixBuffer:
    """Buffer class for visual matrix editing with scrollable R/C headers."""

    def __init__(self, rows=7, cols=21):
        # Display configuration
        self.display_rows = rows  # Rows 0-6 for display (row 7 is status bar)
        self.display_cols = cols

        # Matrix storage: dict of matrix_name -> 2D list of values
        # Default matrices A, B, C, D, E (2x2 each)
        self.matrices = {
            "A": [["0", "0"], ["0", "0"]],
            "B": [["0", "0"], ["0", "0"]],
            "C": [["0", "0"], ["0", "0"]],
            "D": [["0", "0"], ["0", "0"]],
            "E": [["0", "0"], ["0", "0"]]
        }
        self.matrix_names = ["A", "B", "C", "D", "E"]

        # Current state
        self.current_matrix = "A"

        # Cursor position within matrix (row, col)
        self.cell_row = 0
        self.cell_col = 0

        # Display scroll position for large matrices
        self.display_start_row = 0
        self.display_start_col = 0

        # Cell editing state - always editing the current cell
        self.cell_text = ""
        self.cell_cursor = 0
        self.cell_overwrite = True
        self.cell_overflow = False

        # Display buffer
        self.display_buffer = []
        self.refresh_rows = (0, self.display_rows)

        # Visible grid dimensions (row 0 header + data rows)
        # Row 0: column headers (.  C1  C2  C3  C4)
        # Rows 1-6: matrix data (R1  val val val val)
        self.visible_data_rows = 6  # R1-R6
        self.visible_cols = 4  # C1-C4 (each cell ~5 chars)

        # Mode: 'cell' (editing cells)
        self.mode = 'cell'

        # Result mode: read-only display without "Save matrix" option
        self.result_mode = False

        self._load_cell_text()
        self._update_display_buffer()

    def _load_cell_text(self):
        """Load current cell's value into edit text."""
        matrix = self.matrices[self.current_matrix]
        if self.cell_row < len(matrix) and self.cell_col < len(matrix[0]):
            self.cell_text = matrix[self.cell_row][self.cell_col]
            if self.cell_text == "0":
                self.cell_text = ""
            self.cell_cursor = len(self.cell_text)
            self.cell_overwrite = True
            self.cell_overflow = len(self.cell_text) > 2

    def _save_cell_text(self):
        """Save edit text back to current cell."""
        matrix = self.matrices[self.current_matrix]
        if self.cell_row < len(matrix) and self.cell_col < len(matrix[0]):
            value = self.cell_text.strip()
            if value == "":
                value = "0"
            matrix[self.cell_row][self.cell_col] = value

    def get_matrix(self, name):
        """Get a matrix by name."""
        return self.matrices.get(name)

    def set_matrix(self, name, matrix):
        """Set a matrix by name."""
        self.matrices[name] = matrix
        if name not in self.matrix_names:
            self.matrix_names.append(name)

    def get_matrix_size(self, name):
        """Get (rows, cols) of a matrix."""
        m = self.matrices.get(name)
        if m:
            return (len(m), len(m[0]) if m else 0)
        return (0, 0)

    def resize_matrix(self, name, new_rows, new_cols):
        """Resize a matrix, preserving existing values where possible."""
        if name not in self.matrices:
            # Create new matrix
            self.matrices[name] = [["0" for _ in range(new_cols)] for _ in range(new_rows)]
            if name not in self.matrix_names:
                self.matrix_names.append(name)
            return

        old_matrix = self.matrices[name]
        old_rows = len(old_matrix)
        old_cols = len(old_matrix[0]) if old_rows > 0 else 0

        new_matrix = []
        for r in range(new_rows):
            row = []
            for c in range(new_cols):
                if r < old_rows and c < old_cols:
                    row.append(old_matrix[r][c])
                else:
                    row.append("0")
            new_matrix.append(row)
        self.matrices[name] = new_matrix

        # Reset cursor if out of bounds
        if self.cell_row >= new_rows:
            self.cell_row = new_rows - 1
        if self.cell_col >= new_cols:
            self.cell_col = new_cols - 1

    def add_matrix(self, name):
        """Add a new matrix with default 2x2 size."""
        if name not in self.matrices:
            self.matrices[name] = [["0", "0"], ["0", "0"]]
            self.matrix_names.append(name)
            if not self.current_matrix:
                self.switch_matrix(name)
            return True
        return False

    def delete_matrix(self, name):
        """Delete a matrix."""
        if name in self.matrices:
            del self.matrices[name]
            self.matrix_names.remove(name)
            if self.current_matrix == name:
                if self.matrix_names:
                    self.switch_matrix(self.matrix_names[0])
                else:
                    self.current_matrix = ""
                    self.cell_text = ""
                    self.cell_cursor = 0
                    self.display_start_row = 0
                    self.display_start_col = 0
                    self.refresh_rows = (0, self.display_rows)
            return True
        return False

    def switch_matrix(self, name):
        """Switch to editing a different matrix."""
        if name in self.matrices:
            self.current_matrix = name
            self.cell_row = 0
            self.cell_col = 0
            self.display_start_row = 0
            self.display_start_col = 0
            self.mode = 'cell'
            self._load_cell_text()
            self._update_display_buffer()

    def reset_all(self):
        """Reset all matrices to default 2x2 with zeros."""
        self.matrices = {
            "A": [["0", "0"], ["0", "0"]],
            "B": [["0", "0"], ["0", "0"]],
            "C": [["0", "0"], ["0", "0"]],
            "D": [["0", "0"], ["0", "0"]],
            "E": [["0", "0"], ["0", "0"]]
        }
        self.matrix_names = ["A", "B", "C", "D", "E"]
        self.current_matrix = "A"
        self.cell_row = 0
        self.cell_col = 0
        self.display_start_row = 0
        self.display_start_col = 0
        self.mode = 'cell'
        self._load_cell_text()
        self._update_display_buffer()

    def update_buffer(self, inp):
        """Handle input for matrix editing."""
        matrix = self.matrices[self.current_matrix]
        num_rows = len(matrix)
        num_cols = len(matrix[0]) if num_rows > 0 else 0

        # Cell editing mode - direct typing
        if inp == "nav_u":
            self._save_cell_text()
            if self.cell_row > 0:
                self.cell_row -= 1
                self._update_scroll_position()
            self._load_cell_text()

        elif inp == "nav_d":
            self._save_cell_text()
            if self.cell_row < num_rows - 1:
                self.cell_row += 1
                self._update_scroll_position()
                self._load_cell_text()

        elif inp == "nav_l":
            if self.cell_col > 0:
                # Move to previous column (cell-by-cell)
                self._save_cell_text()
                self.cell_col -= 1
                self._update_scroll_position()
                self._load_cell_text()

        elif inp == "nav_r":
            if self.cell_col < num_cols - 1:
                # Move to next column (cell-by-cell)
                self._save_cell_text()
                self.cell_col += 1
                self._update_scroll_position()
                self._load_cell_text()

        elif inp == "nav_b":
            # Backspace
            if self.cell_cursor > 0:
                self.cell_text = self.cell_text[:self.cell_cursor - 1] + self.cell_text[self.cell_cursor:]
                self.cell_cursor -= 1
                if len(self.cell_text) <= 2:
                    self.cell_overflow = False

        elif inp == "AC":
            # Clear cell text
            self.cell_text = ""
            self.cell_cursor = 0
            self.cell_overflow = False

        elif inp == "ok":
            # Open full editor
            self._update_display_buffer()
            return "edit_cell"

        elif inp and len(inp) >= 1 and inp not in ["alpha", "beta", "home", "menu", "back"]:
            # Add character to cell text
            for char in inp:
                if self.cell_overwrite:
                    self.cell_text = ""
                    self.cell_cursor = 0
                    self.cell_overwrite = False
                self.cell_text = self.cell_text[:self.cell_cursor] + char + self.cell_text[self.cell_cursor:]
                self.cell_cursor += 1
                if len(self.cell_text) > 2:
                    self.cell_overflow = True
                    return "edit_cell"

        self.refresh_rows = (0, self.display_rows)
        self._update_display_buffer()
        return None

    def _update_scroll_position(self):
        """Update scroll position to keep cursor visible."""
        # Vertical scroll
        if self.cell_row < self.display_start_row:
            self.display_start_row = self.cell_row
        elif self.cell_row >= self.display_start_row + self.visible_data_rows:
            self.display_start_row = self.cell_row - self.visible_data_rows + 1

        # Horizontal scroll
        if self.cell_col < self.display_start_col:
            self.display_start_col = self.cell_col
        elif self.cell_col >= self.display_start_col + self.visible_cols:
            self.display_start_col = self.cell_col - self.visible_cols + 1

    def _update_display_buffer(self):
        """Build display buffer for current state - grid view with R/C headers."""
        self.display_buffer = []
        self._build_matrix_display()

    def _build_matrix_display(self):
        """Build display buffer showing matrix grid with R/C headers."""
        matrix = self.matrices[self.current_matrix]
        num_rows = len(matrix)
        num_cols = len(matrix[0]) if num_rows > 0 else 0

        # In result mode, show 6 data rows (no save option)
        # In edit mode, show 5 data rows + save option
        data_rows = 6 if self.result_mode else self.visible_data_rows

        # Row 0: Column headers (.  C1  C2  C3  C4)
        col_header = ".   "  # Corner label (4 chars for "Rx| ")
        for c in range(self.display_start_col, min(self.display_start_col + self.visible_cols, num_cols)):
            col_label = f"C{c+1}"  # 1-indexed
            col_header += col_label.center(5)
        col_header = col_header[:self.display_cols].ljust(self.display_cols)
        self.display_buffer.append(col_header)

        # Rows 1-5 (or 1-6 in result mode): Matrix data (R1| val  val  val  val)
        for r in range(data_rows):
            matrix_row = self.display_start_row + r
            if matrix_row < num_rows:
                row_label = f"R{matrix_row+1}"  # 1-indexed
                line = row_label.ljust(3) + "|"
                for c in range(self.display_start_col, min(self.display_start_col + self.visible_cols, num_cols)):
                    # Get cell value - use edit text if this is current cell
                    if matrix_row == self.cell_row and c == self.cell_col and self.mode == 'cell' and not self.result_mode:
                        cell_val = self.cell_text if self.cell_text else "_"
                    else:
                        cell_val = matrix[matrix_row][c]
                    # Format value to fit (result only)
                    if self.result_mode:
                        cell_val = self._format_cell_value(cell_val)
                    else:
                        if len(cell_val) > 2:
                            cell_val = cell_val[:2]
                    cell_str = cell_val.center(5)
                    line += cell_str
                line = line[:self.display_cols].ljust(self.display_cols)
            else:
                line = " " * self.display_cols
            self.display_buffer.append(line)

        # No save-row in edit mode (auto-save)

    def buffer(self):
        """Return display buffer."""
        return self.display_buffer

    def cursor(self):
        """Return cursor row in display (for highlighting)."""
        # Cursor row in matrix display (1-indexed for data rows, +1 for header)
        return self.cell_row - self.display_start_row + 1

    def cursor_col(self):
        """Return cursor column position for cell highlighting."""
        if self.mode == 'cell':
            # Calculate column position in display
            col_offset = self.cell_col - self.display_start_col
            return 4 + (col_offset * 5)  # 4 chars for "Rx|", 5 chars per cell
        return -1  # No cell highlight in save mode

    def ref_ar(self):
        """Return refresh rows tuple."""
        return self.refresh_rows

    def is_editing_cell(self):
        """Return True if currently editing a cell."""
        return self.mode == 'cell'

    def get_cell_cursor(self):
        """Return cursor position within cell text."""
        if not self.cell_text:
            return 0
        last_idx = max(0, len(self.cell_text) - 1)
        return min(self.cell_cursor, last_idx)

    def get_display_cell_value(self):
        """Return current cell value as displayed."""
        cell_val = self.cell_text if self.cell_text else "_"
        if len(cell_val) > 4:
            cell_val = cell_val[:3] + "."
        return cell_val

    def get_cell_cursor_offset(self):
        """Return cursor offset within 5-char cell for centered display."""
        cell_val = self.get_display_cell_value()
        return max(0, (5 - len(cell_val)) // 2)

    def _format_cell_value(self, cell_val):
        if cell_val == "_":
            return cell_val
        try:
            cell_val = f"{float(cell_val):.1f}"
        except Exception:
            pass
        if len(cell_val) > 5:
            cell_val = cell_val[:5]
        return cell_val

    def get_cell_text(self):
        """Return current cell text being edited."""
        return self.cell_text

    def get_current_matrix_name(self):
        """Return name of current matrix being edited."""
        return self.current_matrix

    def get_all_matrix_names(self):
        """Return list of all matrix names."""
        return self.matrix_names[:]

    def is_save_mode(self):
        """Return True if cursor is on Save matrix option."""
        return False

    def set_result_mode(self, enabled):
        """Enable/disable result mode (read-only, no save option)."""
        self.result_mode = enabled
        self.visible_data_rows = 6
        self._update_display_buffer()

    def update(self):
        """Reset buffer state for current matrix."""
        self.cell_row = 0
        self.cell_col = 0
        self.display_start_row = 0
        self.display_start_col = 0
        self.mode = 'cell'
        self._load_cell_text()
        self._update_display_buffer()
        self.refresh_rows = (0, self.display_rows)
