from data_modules.object_handler import keypad_state_manager, display, typer, app
# import time   

def create_new():
    display.clear_display()
    menu_list=["create_new_1", "create_new_2", "create_new_3", "create_new_4"]
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