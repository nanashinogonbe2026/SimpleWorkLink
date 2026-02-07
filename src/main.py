import flet as ft
from database import Database
from ui.login_view import LoginView
from ui.home_view import HomeView
from ui.requests_form import RequestsForm
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

    print(f"DEBUG: Initial route is {page.route}")

    def route_change(route):
        print(f"DEBUG: Route changed to {route.route}")
        page.views.clear()
        
        # Login Route
        if page.route == "/":
            print("DEBUG: Rendering Login View")
            page.views.append(
                LoginView(page, on_login)
            )
        
        # Home Route (Field Worker)
        elif page.route == "/home":
            print("DEBUG: Rendering Home View")
            if not state.user_id:
                print("DEBUG: No user ID, redirecting to /")
                page.go("/")
                return
            
            page.views.append(
                HomeView(
                    page, 
                    db, 
                    state.user_id, 
                    state.user_name,
                    on_navigate_requests=lambda: page.go("/requests"),
                    on_logout=logout
                )
            )

        # Requests Route
        elif page.route == "/requests":
            print("DEBUG: Rendering Requests View")
            if not state.user_id:
                page.go("/")
                return

            # RequestsForm is currently defined as a function returning a Control, not a full View wrapper.
            # We wrap it in a View here.
            page.views.append(
                ft.View(
                    "/requests",
                    [
                        RequestsForm(
                            page, 
                            db, 
                            state.user_id, 
                            on_back=lambda _: page.go("/home")
                        )
                    ]
                )
            )

        # Admin Route
        elif page.route == "/admin":
            print("DEBUG: Rendering Admin View")
            if not state.user_id or state.user_role != "管理":
                page.go("/")
                return

            # AdminDashboard is also a functional component returning a Control
            page.views.append(
                ft.View(
                    "/admin",
                    [
                        AdminDashboard(
                            page, 
                            db, 
                            on_back=lambda _: logout() # Back from admin logs out or goes to home? Let's say Logout for now as it's a separate role
                        )
                    ]
                )
            )
        
        print(f"DEBUG: Updating page with {len(page.views)} views")
        page.update()

    def view_pop(view):
        print("DEBUG: View pop")
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def on_login(user_id, role):
        print(f"DEBUG: Login user={user_id}, role={role}")
        state.user_id = user_id
        state.user_role = role
        # Simple name lookup (In real app, fetch from DB)
        state.user_name = "山田 太郎" if role == "現場" else "鈴木 一郎"
        
        if role == "現場":
            page.go("/home")
        elif role == "管理":
            page.go("/admin")

    def logout():
        print("DEBUG: Logout")
        state.user_id = None
        state.user_role = None
        state.user_name = None
        page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Initialize the view by manually triggering route change
    route_change(ft.RouteChange(page.route))

if __name__ == "__main__":
    ft.app(target=main)
