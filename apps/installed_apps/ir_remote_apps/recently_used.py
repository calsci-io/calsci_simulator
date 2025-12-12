from data_modules.object_handler import keypad_state_manager, display, typer, app
# import time   

def recently_used():
    display.clear_display()

    menu_list=["recently_used_1", "recently_used_2"]

    menu.menu_list=menu_list
    menu.update()
    menu_refresh.refresh()
    try:
        while True:
            inp = typer.start_typing()
            
            if inp == "back":
                app.set_app_name("ir_remote")
                app.set_group_name("installed_apps")
                break

            elif inp =="ok":
                pass
                # app.set_app_name(menu.menu_list[menu.menu_cursor])
                # app.set_group_name("installed_apps.ir_remote_apps")

            menu.update_buffer(inp)
            menu_refresh.refresh()
            
    except Exception as e:
        print(f"Error: {e}")