import flet as ft
from database import Database
from ui.login_view import LoginView
from ui.home_view import HomeView
from ui.requests_form import RequestsFormView
from ui.admin_dashboard import AdminDashboard

# Initialize Database
db = Database()

def main(page: ft.Page):
    page.title = "Simple-Work-Link"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F4F8"
    
    # Responsive window size for testing
    page.window_width = 400
    page.window_height = 800

    # Application State
    class AppState:
        user_id = None
        user_role = None
        user_name = None

    state = AppState()


    # --- MANUAL ROUTING SYSTEM ---
    # Flet's native routing (page.views) is failing in this environment.
    # We will use direct page manipulation (page.clean + page.add).

    def navigate(route):
        print(f"DEBUG: Navigating to {route}")
        page.clean()
        # Overlay controls must be cleared too as they are persistent
        page.overlay.clear()
        
        # Reset standard page properties
        page.appbar = None
        page.floating_action_button = None
        
        try:
            # Login View
            if route == "/login":
                # LoginView now returns a Container directly
                login_container = LoginView(page, db, on_login)
                page.add(login_container)
            
            # Home View
            elif route == "/home":
                if not state.user_id:
                    navigate("/login")
                    return
                
                # HomeView now returns a Container (with embedded custom App bar logic)
                home_container = HomeView(
                    page, 
                    db, 
                    state.user_id, 
                    state.user_name,
                    on_navigate_requests=lambda: navigate("/requests"),
                    on_logout=logout
                )
                page.add(home_container)

            # Requests View
            elif route == "/requests":
                if not state.user_id:
                    navigate("/login")
                    return
                
                # RequestsFormView returns a Control, so we wrap it or add directly
                req_form = RequestsFormView(
                    page, 
                    db, 
                    state.user_id, 
                    on_back=lambda _: navigate("/home")
                )
                page.add(req_form)

            # Admin View
            elif route == "/admin":
                if not state.user_id or state.user_role != "管理":
                    navigate("/login")
                    return
                
                admin_dash = AdminDashboard(
                    page, 
                    db, 
                    on_back=lambda _: logout()
                )
                page.add(admin_dash)
            
            page.update()
            
        except Exception as e:
            print(f"CRITICAL RENDERING ERROR: {e}")
            with open("error.txt", "w", encoding="utf-8") as f:
                f.write(str(e))
            page.add(ft.Text(f"Error rendering {route}: {e}", color="red", size=20))
            page.update()

    def on_login(user_id, role):
        print(f"DEBUG: Login user={user_id}, role={role}")
        # DBからユーザー名を取得（新規追加ユーザーにも対応）
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        state.user_id = user_id
        state.user_role = role
        state.user_name = result[0] if result else "不明"
        
        if role == "現場":
            navigate("/home")
        elif role == "管理":
            navigate("/admin")

    def logout():
        state.user_id = None
        state.user_role = None
        state.user_name = None
        navigate("/login")

    # Start the app
    navigate("/login")

if __name__ == "__main__":
    ft.app(target=main)
