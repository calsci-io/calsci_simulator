from __future__ import annotations

import importlib.util
import os
from pathlib import Path


def _resolve_calsci_dir():
    override = os.environ.get("CALSCI_APP_DIR")
    if override:
        candidate = Path(override).expanduser().resolve()
        if (candidate / "process_modules" / "menu_buffer_uploader.py").is_file():
            return candidate

    simulator_dir = Path(__file__).resolve().parents[1]
    for candidate in (
        simulator_dir / "calsci_latest_itr",
        simulator_dir.parent / "calsci_latest_itr",
    ):
        if (candidate / "process_modules" / "menu_buffer_uploader.py").is_file():
            return candidate

    raise RuntimeError("calsci_latest_itr directory not found")


def _load_upstream_module():
    module_path = _resolve_calsci_dir() / "process_modules" / "menu_buffer_uploader.py"
    spec = importlib.util.spec_from_file_location(
        "_calsci_latest_itr_process_modules_menu_buffer_uploader",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load upstream menu_buffer_uploader module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_UPSTREAM = _load_upstream_module()

for _name in dir(_UPSTREAM):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_UPSTREAM, _name)

_UPSTREAM.LIST_H = 45
LIST_H = _UPSTREAM.LIST_H


class Tbf(_UPSTREAM.Tbf):
    def _draw_scrollbar(self, item_count, top_index):
        track_x = _UPSTREAM.LIST_X + _UPSTREAM.LIST_W - _UPSTREAM.SCROLL_W - 2
        track_y = _UPSTREAM.LIST_Y + 2
        track_h = _UPSTREAM.LIST_H - 4

        self._rect(track_x, track_y, _UPSTREAM.SCROLL_W, track_h, 1)

        if item_count <= _UPSTREAM.VISIBLE_ROWS:
            thumb_h = track_h - 2
            thumb_y = track_y + 1
        else:
            thumb_h = max(8, ((track_h - 2) * _UPSTREAM.VISIBLE_ROWS) // item_count)
            max_top = item_count - _UPSTREAM.VISIBLE_ROWS
            thumb_range = max(0, (track_h - 2) - thumb_h)
            thumb_y = track_y + 1 + (top_index * thumb_range // max_top)

        self._fill_rect(track_x + 1, thumb_y, max(1, _UPSTREAM.SCROLL_W - 2), thumb_h, 1)

    def _draw_footer(self, state=""):
        state = str(state or "")
        if state == "":
            return
        self._fill_rect(0, _UPSTREAM.STATUS_Y, _UPSTREAM.DISPLAY_WIDTH, 8, 1)
        self._draw_text_center(state, _UPSTREAM.STATUS_Y, color=0)
