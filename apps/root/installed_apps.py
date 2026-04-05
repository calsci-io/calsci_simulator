import st7565 as display

try:
    import tools

    if hasattr(display, "graphics") and not hasattr(display.graphics, "pixels_changed"):
        display.graphics = tools.refresh(display.graphics, pixels_changed=200)
except Exception:
    pass

import machine
from data_modules.object_handler import (
    app,
    apps_installer,
    display,
    keypad_state_manager,
    menu,
    menu_refresh,
    nav,
    typer,
)
from process_modules import boot_up_data_update


_LOCAL_EXTRA_APPS = ("table_buffer_demo", "buffer_scroll_demo")


def _menu_apps():
    app_names = list(apps_installer.get_group_apps())
    for app_name in reversed(_LOCAL_EXTRA_APPS):
        if app_name not in app_names:
            app_names.insert(0, app_name)
    return app_names


def installed_apps():
    display.clear_display()
    menu.menu_list = _menu_apps()
    menu.update()
    menu_refresh.refresh()

    try:
        while True:
            inp = typer.start_typing()
            if inp == "back":
                app.set_app_name("home")
                app.set_group_name("root")
                break
            elif inp in ("alpha", "beta"):
                keypad_state_manager(x=inp)
                menu.update_buffer("")
            elif inp == "off":
                boot_up_data_update.main()
                machine.deepsleep()
            elif inp == "ok":
                app.set_app_name(menu.menu_list[menu.menu_cursor])
                app.set_group_name("installed_apps")
                break
            menu.update_buffer(inp)
            menu_refresh.refresh(state=nav.current_state())
    except Exception as exc:
        print("Error:", exc)
