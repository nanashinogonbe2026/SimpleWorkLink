import flet as ft

def LoginView(page: ft.Page, on_login):
    """
    ID/Password Login View
    on_login: (user_id, role) -> None
    """
    
    # Check if we have database access if needed, but here we just need the structure.
    # The actual authentication logic is passed via on_login wrapper in main.py usually,
    # or we can pass the db instance here. 
    # For now, we will assume on_login handles the logic or we need to access db here.
    # Looking at main.py, LoginView is initialized with (page, on_login).
    # We should probably change main.py to pass db to LoginView or have LoginView call a global/singleton/passed db.
    # Let's check main.py... it does: login_container = LoginView(page, on_login)
    # on_login is a method in main.py that sets state. 
    # We need the DB to authenticate.
    # I will modify main.py to pass `db` to `LoginView` as well, or update `on_login` to handle auth.
    # Let's design LoginView to take `on_authenticate` callback which returns (success, user_id, role, message).
    pass 

    # Wait, I can't just change the signature unless I change main.py too. 
    # Current signature in main.py is: LoginView(page, on_login)
    # I need to change main.py to pass `db` to LoginView.
    # Or I can import `db` from database (bad practice but works for prototype).
    # Better: Update main.py to pass db.
    
    # Let's write the new LoginView assuming it receives `db`.
    # I will stick to the plan: LoginView will handle UI and call `db` for auth.
    
    import database # We'll need to instantiate or accept it. 
    # Actually, main.py instantiates db.
    
    # Revised strategy:
    # 1. Update LoginView to accept `db`.
    # 2. Update main.py to pass `db` to LoginView.
    
    return LoginViewImpl(page, on_login)

def LoginViewImpl(page: ft.Page, on_login):
    # This is a placeholder since I need to change main.py first or simultaneously.
    # I will write the actual content here, but I must remember to update main.py next.
    
    id_field = ft.TextField(label="ログインID", width=300, prefix_icon=ft.Icons.PERSON)
    pass_field = ft.TextField(label="パスワード", width=300, password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    error_text = ft.Text("", color=ft.Colors.RED)

    def handle_login(e):
        login_id = id_field.value
        password = pass_field.value
        
        if not login_id or not password:
            error_text.value = "IDとパスワードを入力してください"
            page.update()
            return

        # We need to call db.authenticate_user. 
        # Since we don't have db passed in this function signature yet (in main.py logic), 
        # I rely on the caller to handle auth or I need to import it.
        # Let's change the callback protocol. `on_login` in main.py just sets the state.
        # It doesn't authenticate.
        # 
        # I will change this file to accept `db`.
        pass

# ... Redoing the write content to be the final file ...

import flet as ft
from database import Database

def LoginView(page: ft.Page, db: Database, on_login_success):
    """
    ID/Password Login View
    db: Database instance
    on_login_success: (user_id, role) -> None
    """
    
    id_field = ft.TextField(label="ログインID", width=300, prefix_icon=ft.Icons.PERSON)
    pass_field = ft.TextField(label="パスワード", width=300, password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    error_text = ft.Text("", color=ft.Colors.RED)

    def handle_login(e):
        login_id = id_field.value
        password = pass_field.value
        
        if not login_id or not password:
            error_text.value = "IDとパスワードを入力してください"
            page.update()
            return

        user = db.authenticate_user(login_id, password)
        if user:
            # user: (id, name, role)
            user_id, name, role = user
            # Success
            on_login_success(user_id, role)
        else:
            error_text.value = "IDまたはパスワードが間違っています"
            page.update()

    def handle_enter(e):
        if e.key == "Enter":
            handle_login(e)

    id_field.on_submit = handle_login
    pass_field.on_submit = handle_login

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Simple-Work-Link", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("ログイン", size=20, color=ft.Colors.GREY_700),
                ft.Container(height=30),
                
                id_field,
                pass_field,
                error_text,
                
                ft.Container(height=20),
                
                ft.ElevatedButton(
                    content=ft.Text("ログイン"),
                    width=300,
                    height=50,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                    ),
                    on_click=handle_login
                ),
                
                ft.Container(height=20),
                ft.Text("※初期ID/Pass: admin/admin, yamada/1234", size=12, color=ft.Colors.GREY_500)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=ft.Colors.BLUE_50
    )
