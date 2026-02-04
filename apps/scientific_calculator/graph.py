import framebuf # type: ignore
import math
import utime as time  # type:ignore
from data_modules.object_handler import display, form, nav, text, text_refresh, form_refresh, typer, keypad_state_manager, keypad_state_manager_reset
from data_modules.object_handler import current_app
import gc
try:
    import gc_mock  # type: ignore  # Extends gc with MicroPython functions for simulator
except:
    pass

eval_globals = {
    # Functions
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'atan2': math.atan2,
    'ceil': math.ceil,
    'copysign': math.copysign,
    'degrees': math.degrees,
    'exp': math.exp,
    'fabs': math.fabs,
    'floor': math.floor,
    'fmod': math.fmod,
    'frexp': math.frexp,
    'ldexp': math.ldexp,
    'log': math.log,
    'modf': math.modf,
    'pow': math.pow,
    'radians': math.radians,
    'sqrt': math.sqrt,
    'trunc': math.trunc,
    
    # Constants
    'pi': math.pi,
    'e': math.e,
}

# Graph configuration for consistent experience
GRAPH_CONFIG = {
    'zoom_in': 0.8,
    'zoom_out': 1.25,
    'pan_shift': 0.15,
    'base_samples_per_px': 3,   # Minimum samples per pixel
    'zoom_quality_factor': 6,   # Extra quality at high zoom
    'refine_samples': 12,       # Extra samples in rapid change regions
    'max_jump_fraction': 0.2,   # Break lines if jump exceeds this
    'min_segment_length': 2,
    'transition_steps': 6,
    'transition_delay_ms': 15,
    'bottom_margin': 8,
    'smart_ticks': True,
    'adaptive_increase': 4,     # Multiplier for increasing samples (higher = more aggressive)
    'adaptive_decrease': 5,     # Divisor for decreasing samples (higher = less aggressive)
}

# Cursor state
class CursorState:
    def __init__(self):
        self.mode = 'none'  # 'none', 'x', 'y', 'both'
        self.x_pixel = 64   # Center x position
        self.y_pixel = 28   # Center y position (considering bottom margin)

    def toggle_mode(self):
        """Cycle through cursor modes: none -> x -> y -> both -> none"""
        modes = ['none', 'x', 'y', 'both']
        current_idx = modes.index(self.mode)
        self.mode = modes[(current_idx + 1) % len(modes)]

    def toggle_active(self):
        """Toggle cursor visibility (none <-> both)."""
        self.mode = 'both' if self.mode == 'none' else 'none'

    def move(self, direction, width=128):
        """Move cursor along x only (y will follow the function)."""
        if direction == 'left' and self.x_pixel > 0:
            self.x_pixel -= 1
            return True
        if direction == 'right' and self.x_pixel < width - 1:
            self.x_pixel += 1
            return True
        return False


def format_number(value):
    pi_multiple = value / math.pi
    if abs(pi_multiple - round(pi_multiple)) < 0.001:  
        multiple = round(pi_multiple)
        if multiple == 0:
            return "0 "
        elif multiple == 1:
            return "pi "
        elif multiple == -1:
            return "-pi "
        else:
            return f"{multiple}*pi "
    return f"{value:.2f} "

class SmallCharacters:
    Chr3x5_data = {
        # Letters
        "x": [0x05, 0x02, 0x05],  # x
        "m": [0x07, 0x06, 0x07],  # m
        "i": [0x00, 0x17, 0x00],  # i
        "n": [0x07, 0x04, 0x07],  # n
        "a": [0x17, 0x15, 0x1F],  # a
        "_": [0x01, 0x01, 0x01],  # _
        " ": [0x00, 0x00, 0x00],  # Space
        "y": [0x1D, 0x05, 0x1F],  # y
        # Digits
        "0": [0x0E, 0x11, 0x0E],  # 0
        "1": [0x04, 0x0C, 0x04],  # 1
        "2": [0x1E, 0x02, 0x1F],  # 2
        "3": [0x1E, 0x0E, 0x1F],  # 3
        "4": [0x11, 0x1F, 0x01],  # 4
        "5": [0x1F, 0x0E, 0x1F],  # 5
        "6": [0x0E, 0x14, 0x0E],  # 6
        "7": [0x1F, 0x02, 0x04],  # 7
        "8": [0x0E, 0x0E, 0x0E],  # 8
        "9": [0x0E, 0x0F, 0x0E],  # 9
        # Symbols
        ".": [0x00, 0x00, 0x04],  # .
        "-": [0x00, 0x1F, 0x00],  # - (wider minus)
        "+": [0x04, 0x0E, 0x04],  # +
    }

    @classmethod
    def get_char(cls, char):
        return cls.Chr3x5_data.get(char, [0x1F, 0x1F, 0x1F])  # Default to solid block if char not found


def draw_small_text(fb, text, x, y):
    """Draw text using the 3x5 font on the framebuffer."""
    for char in text:
        char_data = SmallCharacters.get_char(char)
        for col in range(3):  # 3 pixels wide
            byte = char_data[col]
            for row in range(5):  # 5 pixels tall
                if byte & (1 << (4 - row)):  # Bit is set (1)
                    fb.pixel(x + col, y + row, 1)
        x += 4  # Move 4 pixels to the right for the next character (3 width + 1 space)


class MediumDigits:
    # 5x8 font subset (digits and symbols) for clearer cursor readout
    data = {
        " ": [0x00, 0x00, 0x00, 0x00, 0x00],
        "0": [0x3E, 0x51, 0x49, 0x45, 0x3E],
        "1": [0x00, 0x42, 0x7F, 0x40, 0x00],
        "2": [0x42, 0x61, 0x51, 0x49, 0x46],
        "3": [0x21, 0x41, 0x45, 0x4B, 0x31],
        "4": [0x18, 0x14, 0x12, 0x7F, 0x10],
        "5": [0x27, 0x45, 0x45, 0x45, 0x39],
        "6": [0x3C, 0x4A, 0x49, 0x49, 0x30],
        "7": [0x01, 0x71, 0x09, 0x05, 0x03],
        "8": [0x36, 0x49, 0x49, 0x49, 0x36],
        "9": [0x06, 0x49, 0x49, 0x29, 0x1E],
        ".": [0x00, 0x60, 0x60, 0x00, 0x00],
        "-": [0x08, 0x08, 0x08, 0x08, 0x08],
        "+": [0x08, 0x08, 0x3E, 0x08, 0x08],
        "x": [0x44, 0x28, 0x10, 0x28, 0x44],
        "y": [0x0C, 0x50, 0x50, 0x50, 0x3C],
    }

    @classmethod
    def get_char(cls, char):
        return cls.data.get(char, cls.data[" "])


def draw_medium_text(fb, text, x, y):
    """Draw text using a 5x7 font for clearer numeric display."""
    for char in text:
        char_data = MediumDigits.get_char(char)
        for col in range(5):
            byte = char_data[col]
            for row in range(7):  # 7 rows to fit bottom margin
                if byte & (1 << row):
                    fb.pixel(x + col, y + row, 1)
        x += 6  # 5 width + 1 space


def find_smart_tick_values(min_val, max_val, target_count=8):
    """Find aesthetically pleasing tick mark positions."""
    range_val = max_val - min_val
    if range_val == 0:
        return []

    # Calculate nice step sizes
    rough_step = range_val / target_count
    magnitude = 10 ** math.floor(math.log10(rough_step))

    # Try nice step sizes in order of preference
    nice_steps = [magnitude, 2*magnitude, 5*magnitude, 10*magnitude]
    step = nice_steps[0]
    for s in nice_steps:
        if range_val / s <= target_count:
            step = s
            break

    # Generate tick values
    start = math.ceil(min_val / step) * step
    ticks = []
    val = start
    while val <= max_val and len(ticks) < target_count:
        ticks.append(val)
        val += step

    # Special handling for pi multiples
    pi_ticks = []
    pi_step = math.pi / 2
    if range_val > math.pi * 3:
        pi_step = math.pi
    elif range_val < math.pi:
        pi_step = math.pi / 4

    pi_start = math.ceil(min_val / pi_step) * pi_step
    val = pi_start
    while val <= max_val:
        if abs(val) > 0.01:  # Skip zero
            pi_ticks.append(val)
        val += pi_step

    # Use pi ticks if they look better
    if 3 <= len(pi_ticks) <= target_count:
        return pi_ticks

    return ticks

def is_valid_value(val):
    """Check if value is finite and not NaN."""
    if val != val:  # NaN check
        return False
    try:
        if abs(val) > 1e10:  # Treat very large values as invalid
            return False
    except:
        return False
    return True

def safe_eval(func, exp_str, x):
    """Safely evaluate function, returning None for invalid results."""
    try:
        y = func(exp_str, x)
        if is_valid_value(y):
            return y
    except:
        pass
    return None

def draw_axis_labels(fb, x_min, x_max, y_min, y_max, width, height):
    """Draw numeric labels on axis boundaries."""
    plot_height = height - GRAPH_CONFIG['bottom_margin']

    # Format numbers simply and safely
    def format_label(val):
        try:
            if val == 0:
                return "0"
            # For all numbers, use fixed-point notation with reasonable precision
            if abs(val) > 99:
                return f"{int(val)}"
            elif abs(val) >= 1:
                return f"{val:.1f}"
            elif abs(val) >= 0.1:
                return f"{val:.2f}"
            else:
                return f"{val:.0f}"
        except:
            return "0"

    # Format labels - only use characters we have in SmallCharacters
    try:
        x_min_str = str(format_label(x_min))[:4]
        x_max_str = str(format_label(x_max))[:4]
        y_min_str = str(format_label(y_min))[:4]
        y_max_str = str(format_label(y_max))[:4]
    except:
        x_min_str = "x_mn"
        x_max_str = "x_mx"
        y_min_str = "y_mn"
        y_max_str = "y_mx"

    # Draw X-axis labels at bottom
    if x_min_str:
        draw_small_text(fb, x_min_str, 2, plot_height - 6)
    if x_max_str:
        draw_small_text(fb, x_max_str, width - 13, plot_height - 6)

    # Draw Y-axis labels on right side
    if y_max_str:
        draw_small_text(fb, y_max_str, width - 13, 2)
    if y_min_str:
        draw_small_text(fb, y_min_str, width - 13, plot_height - 12)

def _sleep_ms(ms):
    if hasattr(time, "sleep_ms"):
        time.sleep_ms(ms)
    else:
        time.sleep(ms / 1000.0)

def _mem_free():
    if hasattr(gc, "mem_free"):
        return gc.mem_free()
    return "n/a"

def get_bounds_from_form():
    """Extract bounds from form input."""
    return {
        'x_min': eval(form.inp_list()["inp_1"], eval_globals),
        'x_max': eval(form.inp_list()["inp_2"], eval_globals),
        'y_min': eval(form.inp_list()["inp_3"], eval_globals),
        'y_max': eval(form.inp_list()["inp_4"], eval_globals),
    }

def update_bounds(x_min, x_max, y_min, y_max):
    """Update form with new bounds."""
    form.input_list["inp_1"] = format_number(x_min)
    form.input_list["inp_2"] = format_number(x_max)
    form.input_list["inp_3"] = format_number(y_min)
    form.input_list["inp_4"] = format_number(y_max)

def apply_zoom(bounds, zoom_factor):
    """Apply zoom to bounds and return new bounds."""
    x_range = bounds['x_max'] - bounds['x_min']
    y_range = bounds['y_max'] - bounds['y_min']

    x_center = (bounds['x_min'] + bounds['x_max']) / 2
    y_center = (bounds['y_min'] + bounds['y_max']) / 2

    new_x_range = x_range * zoom_factor
    new_y_range = y_range * zoom_factor

    return {
        'x_min': x_center - new_x_range / 2,
        'x_max': x_center + new_x_range / 2,
        'y_min': y_center - new_y_range / 2,
        'y_max': y_center + new_y_range / 2,
    }

def apply_pan(bounds, direction):
    """Apply pan to bounds and return new bounds. Direction: 'up', 'down', 'left', 'right'."""
    x_range = bounds['x_max'] - bounds['x_min']
    y_range = bounds['y_max'] - bounds['y_min']
    shift = GRAPH_CONFIG['pan_shift']

    new_bounds = bounds.copy()

    if direction == 'up':
        shift_amount = y_range * shift
        new_bounds['y_min'] += shift_amount
        new_bounds['y_max'] += shift_amount
    elif direction == 'down':
        shift_amount = y_range * shift
        new_bounds['y_min'] -= shift_amount
        new_bounds['y_max'] -= shift_amount
    elif direction == 'left':
        shift_amount = x_range * shift
        new_bounds['x_min'] -= shift_amount
        new_bounds['x_max'] -= shift_amount
    elif direction == 'right':
        shift_amount = x_range * shift
        new_bounds['x_min'] += shift_amount
        new_bounds['x_max'] += shift_amount

    return new_bounds

def pan_by_pixels(bounds, dx_px=0, dy_px=0, width=128, height=64):
    """Pan bounds by a pixel delta."""
    new_bounds = bounds.copy()
    x_range = bounds['x_max'] - bounds['x_min']
    y_range = bounds['y_max'] - bounds['y_min']
    if width > 1 and dx_px:
        dx = (x_range / (width - 1)) * dx_px
        new_bounds['x_min'] += dx
        new_bounds['x_max'] += dx
    plot_height = height - GRAPH_CONFIG['bottom_margin']
    if plot_height > 1 and dy_px:
        dy = (y_range / (plot_height - 1)) * dy_px
        new_bounds['y_min'] -= dy
        new_bounds['y_max'] -= dy
    return new_bounds
def draw_cursor(fb, cursor_state, bounds, func, exp_str, width=128, height=64):
    """Draw cursor vertical line and display x and y coordinates."""
    if cursor_state.mode == 'none':
        return

    plot_height = height - GRAPH_CONFIG['bottom_margin']

    x_range = bounds['x_max'] - bounds['x_min']
    y_range = bounds['y_max'] - bounds['y_min']
    if x_range == 0 or y_range == 0 or width < 2 or plot_height < 2:
        return

    # Compute x coordinate at cursor position (can handle float x_pixel for precision)
    x_coord = bounds['x_min'] + (cursor_state.x_pixel / (width - 1)) * x_range

    # Draw vertical cursor line (convert to int for framebuffer drawing)
    fb.vline(int(cursor_state.x_pixel), 0, plot_height, 1)

    # Format and display x value
    def format_coord(val, prefix):
        # Check for pi multiples
        pi_ratio = val / math.pi
        if abs(pi_ratio - round(pi_ratio)) < 0.01 and abs(pi_ratio) < 10:
            n = round(pi_ratio)
            if n == 0:
                return f"{prefix} 0"
            elif n == 1:
                return f"{prefix} 3.14"
            elif n == -1:
                return f"{prefix}-3.14"
            else:
                return f"{prefix}{n}p"

        # Regular formatting
        if abs(val) < 0.01:
            return f"{prefix} 0"
        elif abs(val) < 1:
            return f"{prefix}{val:.2f}"[:8]
        elif abs(val) < 10:
            return f"{prefix}{val:.2f}"[:8]
        elif abs(val) < 100:
            return f"{prefix}{val:.1f}"[:8]
        else:
            return f"{prefix}{int(val)}"[:8]

    x_str = format_coord(x_coord, "x")
    draw_medium_text(fb, x_str, 2, plot_height + 1)

    # Evaluate and display y value at cursor x position
    y_coord = safe_eval(func, exp_str, x_coord)
    if y_coord is not None and is_valid_value(y_coord):
        y_str = format_coord(y_coord, "y")
        # Display on right side below (vertically stacked with axis labels)
        draw_medium_text(fb, y_str, width - 42, plot_height + 1)
    else:
        # Display "undefined" if function is not defined at this x
        draw_medium_text(fb, "y undef", width - 42, plot_height + 1)

def replot_graph(fb, exp_str, bounds, cursor_state=None):
    """Clear and replot the graph with new bounds."""
    fb.fill(0)
    plot_function(fb=fb, func=polynom1, exp_str=exp_str,
                  x_min=bounds['x_min'], x_max=bounds['x_max'],
                  y_min=bounds['y_min'], y_max=bounds['y_max'],
                  width=128, height=64)
    if cursor_state:
        draw_cursor(fb, cursor_state, bounds, polynom1, exp_str)
    display.clear_display()
    display.graphics(fb)

def animate_transition(fb, exp_str, start_bounds, end_bounds, cursor_state=None):
    """Smoothly animate graph between bounds."""
    steps = GRAPH_CONFIG.get('transition_steps', 1)
    delay_ms = GRAPH_CONFIG.get('transition_delay_ms', 0)
    if steps <= 1:
        replot_graph(fb, exp_str, end_bounds, cursor_state)
        return
    for step in range(1, steps + 1):
        t = step / steps
        interp = {
            'x_min': start_bounds['x_min'] + (end_bounds['x_min'] - start_bounds['x_min']) * t,
            'x_max': start_bounds['x_max'] + (end_bounds['x_max'] - start_bounds['x_max']) * t,
            'y_min': start_bounds['y_min'] + (end_bounds['y_min'] - start_bounds['y_min']) * t,
            'y_max': start_bounds['y_max'] + (end_bounds['y_max'] - start_bounds['y_max']) * t,
        }
        replot_graph(fb, exp_str, interp, cursor_state)
        if delay_ms:
            _sleep_ms(delay_ms)


def graph(db={}):
    print("start of graph", _mem_free())
    keypad_state_manager_reset()
    global display, form, form_refresh, typer, nav, current_app, eval_globals
    form.input_list={"inp_0": "x*sin(x) ", "inp_1": "-20 ", "inp_2": "20 ", "inp_3": "-10 ", "inp_4": "10 "}
    form.form_list=["enter function:f(x)", "inp_0", "enter x_min:", "inp_1", "enter x_max:", "inp_2", "enter y_min:", "inp_3", "enter y_max:", "inp_4"]
    form.update()
    form_refresh.refresh()

    buffer1 = bytearray((128 * 64) // 8)
    fb1 = framebuf.FrameBuffer(buffer1, 128, 64, framebuf.MONO_VLSB)

    while True:
        inp = typer.start_typing()
        if inp == "back":
            del buffer1, fb1
            current_app[0]="scientific_calculator"
            current_app[1]="application_modules"

            break

        elif inp == "ok":
            try:
                bounds = get_bounds_from_form()
                cursor_state = CursorState()
                replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
            except:
                continue
            print("after plotting", _mem_free())

            while True:
                inp_breaker = typer.start_typing()

                # Toggle cursor on/off with the physical A key (module/copy/a depending on mode)
                if inp_breaker in ("a", "A", "module", "copy"):
                    cursor_state.toggle_active()
                    replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)

                # Navigation keys behavior depends on cursor mode
                elif inp_breaker == "nav_u":
                    if cursor_state.mode != 'none':
                        cursor_state.move('up')
                        replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                    else:
                        new_bounds = apply_pan(bounds, 'up')
                        animate_transition(fb1, form.inp_list()["inp_0"], bounds, new_bounds, cursor_state)
                        bounds = new_bounds
                        update_bounds(**bounds)

                elif inp_breaker == "nav_d":
                    if cursor_state.mode != 'none':
                        cursor_state.move('down')
                        replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                    else:
                        new_bounds = apply_pan(bounds, 'down')
                        animate_transition(fb1, form.inp_list()["inp_0"], bounds, new_bounds, cursor_state)
                        bounds = new_bounds
                        update_bounds(**bounds)

                elif inp_breaker == "nav_l":
                    if cursor_state.mode != 'none':
                        # Pan graph left (moves viewing window left, function moves right)
                        bounds = pan_by_pixels(bounds, dx_px=-1, width=128, height=64)
                        replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                        update_bounds(**bounds)
                    else:
                        new_bounds = apply_pan(bounds, 'left')
                        animate_transition(fb1, form.inp_list()["inp_0"], bounds, new_bounds, cursor_state)
                        bounds = new_bounds
                        update_bounds(**bounds)

                elif inp_breaker == "nav_r":
                    if cursor_state.mode != 'none':
                        # Pan graph right (moves viewing window right, function moves left)
                        bounds = pan_by_pixels(bounds, dx_px=1, width=128, height=64)
                        replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                        update_bounds(**bounds)
                    else:
                        new_bounds = apply_pan(bounds, 'right')
                        animate_transition(fb1, form.inp_list()["inp_0"], bounds, new_bounds, cursor_state)
                        bounds = new_bounds
                        update_bounds(**bounds)

                elif inp_breaker == "plus":
                    new_bounds = apply_zoom(bounds, GRAPH_CONFIG['zoom_in'])
                    animate_transition(fb1, form.inp_list()["inp_0"], bounds, new_bounds, cursor_state)
                    bounds = new_bounds
                    update_bounds(**bounds)

                elif inp_breaker == "minus":
                    new_bounds = apply_zoom(bounds, GRAPH_CONFIG['zoom_out'])
                    animate_transition(fb1, form.inp_list()["inp_0"], bounds, new_bounds, cursor_state)
                    bounds = new_bounds
                    update_bounds(**bounds)

                elif inp_breaker == "4":
                    # Reduce adaptive sampling
                    GRAPH_CONFIG['adaptive_increase'] = max(1, GRAPH_CONFIG.get('adaptive_increase', 4) - 1)
                    GRAPH_CONFIG['adaptive_decrease'] = min(30, GRAPH_CONFIG.get('adaptive_decrease', 5) + 1)
                    print(GRAPH_CONFIG['adaptive_increase'], GRAPH_CONFIG['adaptive_decrease'])
                    replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)

                elif inp_breaker == "5":
                    # Increase adaptive sampling
                    GRAPH_CONFIG['adaptive_increase'] = min(30, GRAPH_CONFIG.get('adaptive_increase', 4) + 1)
                    GRAPH_CONFIG['adaptive_decrease'] = max(1, GRAPH_CONFIG.get('adaptive_decrease', 5) - 1)
                    print(GRAPH_CONFIG['adaptive_increase'], GRAPH_CONFIG['adaptive_decrease'])
                    replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)

                elif inp_breaker in ("alpha", "beta"):
                    keypad_state_manager(x=inp_breaker)

                elif inp_breaker in ("b", "B", "bluetooth", "paste"):
                    # Input custom X value and center graph on it
                    fb1.fill(0)
                    display.clear_display()

                    # Create temporary form for X input
                    temp_form_list = ["Enter X value:", "inp_temp_x"]
                    temp_input_list = {"inp_temp_x": "0 "}

                    # Save current form state
                    saved_form_list = form.form_list
                    saved_input_list = form.input_list

                    # Set up temporary form
                    form.form_list = temp_form_list
                    form.input_list = temp_input_list
                    form.update()
                    form_refresh.refresh()

                    # Get user input
                    while True:
                        inp_temp = typer.start_typing()
                        if inp_temp == "ok":
                            try:
                                # Get the X value
                                custom_x = eval(form.inp_list()["inp_temp_x"], eval_globals)

                                # Calculate new bounds centered on custom_x
                                x_range = bounds['x_max'] - bounds['x_min']

                                # Update bounds to center on custom X
                                bounds['x_min'] = custom_x - x_range / 2
                                bounds['x_max'] = custom_x + x_range / 2

                                # Position cursor exactly at center (where custom_x will be)
                                # For 128 pixels (0-127), center is at pixel 63.5
                                cursor_state.x_pixel = 63.5  # Exact center for custom X

                                # Enable cursor to show the X value
                                cursor_state.mode = 'both'  # Show cursor at custom X

                                # Restore original form
                                form.form_list = saved_form_list
                                form.input_list = saved_input_list
                                form.update()

                                # Force complete recalculation with new sampling around custom X
                                fb1.fill(0)
                                replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                                update_bounds(**bounds)
                                break
                            except:
                                # Restore form and continue without changes
                                form.form_list = saved_form_list
                                form.input_list = saved_input_list
                                form.update()
                                replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                                break
                        elif inp_temp == "back":
                            # Cancel - restore form
                            form.form_list = saved_form_list
                            form.input_list = saved_input_list
                            form.update()
                            replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                            break
                        elif inp_temp == "alpha" or inp_temp == "beta":
                            keypad_state_manager(x=inp_temp)
                            form.update_buffer("")
                        elif inp_temp not in ["alpha", "beta", "ok"]:
                            form.update_buffer(inp_temp)
                        form_refresh.refresh(state=nav.current_state())

                elif inp_breaker in ("c", "C", "sin(", "asin("):
                    # Set custom delta step (base_samples_per_px)
                    fb1.fill(0)
                    display.clear_display()

                    # Create temporary form for delta input
                    temp_form_list = ["Delta (samples/px):", "inp_temp_delta"]
                    temp_input_list = {"inp_temp_delta": str(GRAPH_CONFIG.get('base_samples_per_px', 3)) + " "}

                    # Save current form state
                    saved_form_list = form.form_list
                    saved_input_list = form.input_list

                    # Set up temporary form
                    form.form_list = temp_form_list
                    form.input_list = temp_input_list
                    form.update()
                    form_refresh.refresh()

                    # Get user input
                    while True:
                        inp_temp = typer.start_typing()
                        if inp_temp == "ok":
                            try:
                                # Get the delta value
                                custom_delta = eval(form.inp_list()["inp_temp_delta"], eval_globals)

                                # Validate and apply (allow any positive value, cap at reasonable maximum)
                                if custom_delta >= 0.1:  # Allow fractional and very fine sampling
                                    # Cap at 100 for performance, but allow flexibility
                                    GRAPH_CONFIG['base_samples_per_px'] = min(custom_delta, 100)
                                    print(f"Delta step set to: {GRAPH_CONFIG['base_samples_per_px']}")

                                # Restore original form
                                form.form_list = saved_form_list
                                form.input_list = saved_input_list
                                form.update()

                                # Force complete recalculation with new delta
                                fb1.fill(0)
                                replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                                break
                            except:
                                # Restore form and continue without changes
                                form.form_list = saved_form_list
                                form.input_list = saved_input_list
                                form.update()
                                replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                                break
                        elif inp_temp == "back":
                            # Cancel - restore form
                            form.form_list = saved_form_list
                            form.input_list = saved_input_list
                            form.update()
                            replot_graph(fb1, form.inp_list()["inp_0"], bounds, cursor_state)
                            break
                        elif inp_temp == "alpha" or inp_temp == "beta":
                            keypad_state_manager(x=inp_temp)
                            form.update_buffer("")
                        elif inp_temp not in ["alpha", "beta", "ok"]:
                            form.update_buffer(inp_temp)
                        form_refresh.refresh(state=nav.current_state())

                elif inp_breaker == "back":
                    break



            fb1.fill(0)
            form.refresh_rows = (0, form.actual_rows)
            display.clear_display()
            form_refresh.refresh()

        elif inp == "alpha" or inp == "beta":
            keypad_state_manager(x=inp)
            form.update_buffer("")
        elif inp not in ["alpha", "beta", "ok"]:
            form.update_buffer(inp)
        form_refresh.refresh(state=nav.current_state())

        time.sleep(0.1)
    print("end of graph", _mem_free())

def plot_function(fb, func, exp_str, x_min, x_max, y_min, y_max, width, height):
    """Advanced plotting with adaptive sampling and edge case handling."""
    global eval_globals

    plot_height = height - GRAPH_CONFIG['bottom_margin']
    if width < 2 or plot_height < 2:
        return

    x_range = x_max - x_min
    y_range = y_max - y_min
    if x_range == 0 or y_range == 0:
        return

    x_scale = x_range / (width - 1)
    y_scale = y_range / (plot_height - 1)

    def map_x(x_val):
        """Map x value to pixel, return None if out of bounds"""
        px = int((x_val - x_min) / x_scale + 0.5)
        if px < 0 or px >= width:
            return None
        return px

    def map_y(y_val):
        """Map y value to pixel, return None if out of bounds"""
        py = int((y_max - y_val) / y_scale + 0.5)
        if py < 0 or py >= plot_height:
            return None
        return py

    def map_x_clamped(x_val):
        """Map x value to pixel with clamping (for axes only)"""
        px = int((x_val - x_min) / x_scale + 0.5)
        return max(0, min(width - 1, px))

    def map_y_clamped(y_val):
        """Map y value to pixel with clamping (for axes only)"""
        py = int((y_max - y_val) / y_scale + 0.5)
        return max(0, min(plot_height - 1, py))

    # Find actual axis positions (use clamped for axes)
    x_axis_y = map_y_clamped(0) if y_min <= 0 <= y_max else -1
    y_axis_x = map_x_clamped(0) if x_min <= 0 <= x_max else -1

    # Draw axes
    if x_axis_y >= 0:
        fb.hline(0, x_axis_y, width, 1)
    if y_axis_x >= 0:
        fb.vline(y_axis_x, 0, plot_height, 1)

    # Smart tick marks (use clamped for ticks)
    if GRAPH_CONFIG.get('smart_ticks', True):
        x_ticks = find_smart_tick_values(x_min, x_max, 12)
        y_ticks = find_smart_tick_values(y_min, y_max, 8)

        # Draw x-axis ticks
        if x_axis_y >= 0:
            for tick_val in x_ticks:
                tick_x = map_x_clamped(tick_val)
                if 0 <= tick_x < width:
                    fb.pixel(tick_x, x_axis_y - 1, 1)

        # Draw y-axis ticks
        if y_axis_x >= 0:
            for tick_val in y_ticks:
                tick_y = map_y_clamped(tick_val)
                if 0 <= tick_y < plot_height:
                    fb.pixel(y_axis_x + 1, tick_y, 1)

    def eval_with_status(x_val):
        """Evaluate and return (y, status) where status is 'valid', 'out_of_bounds', or 'undefined'."""
        y_val = safe_eval(func, exp_str, x_val)
        if y_val is None:
            return (None, 'undefined')
        if y_val < y_min or y_val > y_max:
            return (y_val, 'out_of_bounds')
        return (y_val, 'valid')

    def eval_visible(x_val):
        """Evaluate and return y only if it is valid and within visible bounds."""
        y_val, status = eval_with_status(x_val)
        if status == 'valid':
            return y_val
        return None

    # Phase 1: Zoom-adaptive sampling
    base_samples_per_px = GRAPH_CONFIG.get('base_samples_per_px', 3)
    zoom_factor = GRAPH_CONFIG.get('zoom_quality_factor', 6)
    adaptive_increase = GRAPH_CONFIG.get('adaptive_increase', 4)
    adaptive_decrease = GRAPH_CONFIG.get('adaptive_decrease', 5)

    # Calculate zoom level (smaller range = more zoomed in)
    reference_range = 40.0  # Reference range for normal view
    zoom_level = reference_range / max(x_range, 0.1)

    # Scale sampling based on zoom - more samples when zoomed in
    if zoom_level > 2:
        # Zoomed in - increase quality aggressively
        zoom_boost = min(zoom_level / zoom_factor, adaptive_increase)
        samples_multiplier = 1 + zoom_boost
    elif zoom_level < 0.5:
        # Zoomed out - decrease sampling to save computation
        samples_multiplier = max(0.5, 1.0 / min(adaptive_decrease, (1.0 / zoom_level) / 2))
    else:
        # Normal zoom
        samples_multiplier = 1

    coarse_count = int(width * base_samples_per_px * samples_multiplier)
    coarse_count = max(coarse_count, width * 2)  # Minimum 2 samples per pixel
    coarse_count = min(coarse_count, width * 25) # Maximum 25 samples per pixel for best quality

    coarse_points = []
    coarse_statuses = []
    for i in range(coarse_count):
        x_val = x_min + (x_range * i) / (coarse_count - 1)
        y_val, status = eval_with_status(x_val)

        if status == 'valid':
            coarse_points.append((x_val, y_val, True))
        else:
            coarse_points.append((x_val, None, False))
        coarse_statuses.append(status)

    if sum(1 for _, _, valid in coarse_points if valid) < 2:
        return

    # Phase 2: Identify regions needing refinement
    refine_regions = []
    refine_threshold = 1 if zoom_level > 2 else 2  # Stricter at high zoom

    for i in range(len(coarse_points) - 1):
        x1, y1, valid1 = coarse_points[i]
        x2, y2, valid2 = coarse_points[i + 1]

        needs_refine = False

        # Case 1: Transition from valid to invalid or vice versa (discontinuity)
        if valid1 != valid2:
            needs_refine = True

        # Case 2: Large change in y value (pixel-based)
        elif valid1 and valid2:
            y_px1 = map_y(y1)
            y_px2 = map_y(y2)
            if y_px1 is not None and y_px2 is not None:
                if abs(y_px2 - y_px1) > refine_threshold:
                    needs_refine = True

        # Case 3: Check for curvature (second derivative)
        if not needs_refine and valid1 and valid2 and i > 0:
            x0, y0, valid0 = coarse_points[i - 1]
            if valid0:
                # Estimate curvature using finite differences
                dx1 = x1 - x0
                dx2 = x2 - x1
                if dx1 > 0 and dx2 > 0:
                    slope1 = (y1 - y0) / dx1
                    slope2 = (y2 - y1) / dx2
                    curvature = abs(slope2 - slope1)
                    # High curvature needs refinement
                    if curvature > y_range / (width * 0.5):
                        needs_refine = True

        if needs_refine:
            refine_regions.append((x1, x2))

    # Phase 2.5: Binary search near asymptote/discontinuity boundaries
    # This pushes the last visible point close to the screen edge so curves
    # don't appear to "start" mid-screen at zoom-out levels.
    boundary_points = []
    for i in range(len(coarse_points) - 1):
        s_curr = coarse_statuses[i]
        s_next = coarse_statuses[i + 1]
        x_curr = coarse_points[i][0]
        x_next = coarse_points[i + 1][0]

        # Defined → undefined: find last visible point before boundary
        if s_curr != 'undefined' and s_next == 'undefined':
            lo, hi = x_curr, x_next
            for _ in range(15):
                mid = (lo + hi) / 2
                y_mid, s = eval_with_status(mid)
                if s == 'undefined':
                    hi = mid
                else:
                    lo = mid
                    if s == 'valid':
                        boundary_points.append((mid, y_mid))

        # Undefined → defined: find first visible point after boundary
        elif s_curr == 'undefined' and s_next != 'undefined':
            lo, hi = x_curr, x_next
            for _ in range(15):
                mid = (lo + hi) / 2
                y_mid, s = eval_with_status(mid)
                if s == 'undefined':
                    lo = mid
                else:
                    hi = mid
                    if s == 'valid':
                        boundary_points.append((mid, y_mid))

        # Valid → out_of_bounds: find last visible point at screen edge
        elif s_curr == 'valid' and s_next == 'out_of_bounds':
            lo, hi = x_curr, x_next
            for _ in range(12):
                mid = (lo + hi) / 2
                y_mid, s = eval_with_status(mid)
                if s == 'valid':
                    lo = mid
                    boundary_points.append((mid, y_mid))
                else:
                    hi = mid

        # Out_of_bounds → valid: find first visible point at screen edge
        elif s_curr == 'out_of_bounds' and s_next == 'valid':
            lo, hi = x_curr, x_next
            for _ in range(12):
                mid = (lo + hi) / 2
                y_mid, s = eval_with_status(mid)
                if s == 'valid':
                    hi = mid
                    boundary_points.append((mid, y_mid))
                else:
                    lo = mid

    # Phase 3: Adaptive refinement in problematic regions
    all_points = list(boundary_points)
    refine_samples = GRAPH_CONFIG.get('refine_samples', 12)

    # Scale refinement based on zoom using adaptive parameters
    if zoom_level > 2:
        # Use adaptive_increase to control refinement aggressiveness
        zoom_refine_factor = min(zoom_level / 2, adaptive_increase / 2)
        refine_samples = int(refine_samples * zoom_refine_factor)
    elif zoom_level < 0.5:
        # Reduce refinement when zoomed out
        refine_samples = max(4, int(refine_samples / (adaptive_decrease / 2)))

    for i in range(len(coarse_points)):
        x_val, y_val, valid = coarse_points[i]
        if valid:
            all_points.append((x_val, y_val))

        # Add refined samples in problematic regions
        if i < len(coarse_points) - 1:
            x_next, _, _ = coarse_points[i + 1]

            # Check if this interval needs refinement
            for region_start, region_end in refine_regions:
                if region_start <= x_val < region_end:
                    # Add intermediate samples
                    for j in range(1, refine_samples):
                        x_refined = x_val + (x_next - x_val) * j / refine_samples
                        y_refined, status = eval_with_status(x_refined)
                        # Only add valid points (not undefined, but can be out of bounds for segment detection later)
                        if y_refined is not None and status != 'undefined':
                            all_points.append((x_refined, y_refined))
                    break

    # Sort points by x coordinate
    all_points.sort(key=lambda p: p[0])

    if len(all_points) < 2:
        return

    # Phase 4: Segment detection with zoom-aware discontinuity logic
    max_jump_fraction = GRAPH_CONFIG.get('max_jump_fraction', 0.2)
    # At high zoom, be more tolerant of pixel jumps (smooth curves can have steep slopes)
    if zoom_level > 2:
        max_jump_fraction = min(0.35, max_jump_fraction * (1 + zoom_level / 10))

    max_jump = int(plot_height * max_jump_fraction)
    min_segment_len = GRAPH_CONFIG.get('min_segment_length', 2)

    segments = []
    current_segment = [all_points[0]]

    for i in range(1, len(all_points)):
        x_val, y_val = all_points[i]
        x_prev, y_prev = all_points[i - 1]

        x_px = map_x(x_val)
        y_px = map_y(y_val)
        x_prev_px = map_x(x_prev)
        y_prev_px = map_y(y_prev)

        # Skip points that are out of visible bounds
        if x_px is None or y_px is None or x_prev_px is None or y_prev_px is None:
            # Out of bounds - start new segment
            if len(current_segment) >= min_segment_len:
                segments.append(current_segment)
            current_segment = []
            if x_px is not None and y_px is not None:
                current_segment = [(x_val, y_val)]
            continue

        # Multiple discontinuity checks
        is_discontinuous = False

        # Check 1: Pixel jump too large
        pixel_jump = abs(y_px - y_prev_px)
        if pixel_jump > max_jump:
            # For high zoom, verify this is a real discontinuity
            if zoom_level > 2:
                # Sample midpoint to confirm
                mid_x = (x_val + x_prev) / 2
                mid_y, mid_status = eval_with_status(mid_x)
                if mid_status == 'undefined':
                    # True discontinuity - function is undefined between these points
                    is_discontinuous = True
                elif mid_status == 'valid':
                    # Check if midpoint is roughly between the two values
                    mid_y_px = map_y(mid_y)
                    if mid_y_px is not None:
                        # If midpoint is way off the line, it's discontinuous
                        expected_mid = (y_px + y_prev_px) / 2
                        if abs(mid_y_px - expected_mid) > max_jump / 2:
                            is_discontinuous = True
            else:
                is_discontinuous = True

        # Check 2: Gap in x domain (missed evaluations between points)
        if not is_discontinuous:
            x_gap = x_val - x_prev
            expected_gap = x_range / (coarse_count - 1)
            if x_gap > expected_gap * 2:
                # Check if there are undefined points in between
                mid_x = (x_val + x_prev) / 2
                mid_y, mid_status = eval_with_status(mid_x)
                if mid_status == 'undefined':
                    is_discontinuous = True

        # Check 3: Extreme slope changes (only at normal zoom)
        if not is_discontinuous and zoom_level <= 2 and len(current_segment) >= 3:
            x_prev2, y_prev2 = current_segment[-2]
            slope1 = (y_prev - y_prev2) / (x_prev - x_prev2) if x_prev != x_prev2 else 0
            slope2 = (y_val - y_prev) / (x_val - x_prev) if x_val != x_prev else 0

            # Very large slope change indicates potential discontinuity
            if abs(slope1) > 1e-6 and abs(slope2) > 1e-6:
                slope_ratio = abs(slope2 / slope1)
                if slope_ratio > 20 or slope_ratio < 0.05:
                    # Double check with midpoint
                    mid_x = (x_val + x_prev) / 2
                    mid_y, mid_status = eval_with_status(mid_x)
                    if mid_status == 'undefined':
                        is_discontinuous = True

        if is_discontinuous:
            if len(current_segment) >= min_segment_len:
                segments.append(current_segment)
            current_segment = [(x_val, y_val)]
        else:
            current_segment.append((x_val, y_val))

    if len(current_segment) >= min_segment_len:
        segments.append(current_segment)

    # Phase 5: Draw segments with smart pixel management
    for segment in segments:
        if len(segment) < min_segment_len:
            continue

        # Convert segment to pixel coordinates
        pixel_coords = []
        for x_val, y_val in segment:
            x_px = map_x(x_val)
            y_px = map_y(y_val)
            if x_px is not None and y_px is not None:
                pixel_coords.append((x_px, y_px))

        if len(pixel_coords) < 2:
            # Single point - just draw it
            if len(pixel_coords) == 1:
                fb.pixel(pixel_coords[0][0], pixel_coords[0][1], 1)
            continue

        # Deduplicate consecutive identical pixels
        unique_pixels = [pixel_coords[0]]
        for i in range(1, len(pixel_coords)):
            if pixel_coords[i] != pixel_coords[i-1]:
                unique_pixels.append(pixel_coords[i])

        # Draw lines between consecutive unique pixels
        for i in range(len(unique_pixels)):
            x_px, y_px = unique_pixels[i]

            if i == 0:
                # First pixel
                fb.pixel(x_px, y_px, 1)
            else:
                x_prev_px, y_prev_px = unique_pixels[i-1]

                # Check if jump is reasonable
                dx = abs(x_px - x_prev_px)
                dy = abs(y_px - y_prev_px)

                if dy <= max_jump or (dx <= 2 and dy <= plot_height // 2):
                    # Draw connecting line
                    fb.line(x_prev_px, y_prev_px, x_px, y_px, 1)
                else:
                    # Too large jump - just draw pixel
                    fb.pixel(x_px, y_px, 1)


def polynom1(exp, x):
    global eval_globals
    # Add 'x' to the dictionary for evaluation
    eval_globals["x"]=x
    # Combine global and local dictionaries
    # context = eval_globals + eval_locals
    # Evaluate the expression
    y = eval(exp, eval_globals)

    return y
