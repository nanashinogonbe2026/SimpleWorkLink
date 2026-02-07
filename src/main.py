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


    print(f"DEBUG: Initial route is '{page.route}'")

    def route_change(route_event):
        # Handle both RouteChangeEvent and Page object (duck typing)
        # Some versions might pass the event, some might rely on page.route
        current_route = route_event.route if hasattr(route_event, 'route') else page.route
        print(f"DEBUG: Route changed to '{current_route}'")
        
        page.views.clear()
        
        # Root Route -> Redirect to Login
        if current_route == "/" or current_route == "":
            print("DEBUG: Root route detected, redirecting to /login")
            page.go("/login")
            return

        # Login Route
        if current_route == "/login":
            print("DEBUG: Rendering Login View")
            try:
                # DEBUG: Simplifying view to check if anything renders
                page.views.append(
                    ft.View(
                        "/login",
                        [
                            ft.AppBar(title=ft.Text("Login Debug")),
                            ft.Text("Login View Debug - Can you see this?", size=30, color="red"),
                            LoginView(page, on_login).controls[0] # Try to append the original content too
                        ]
                    )
                )
            except Exception as e:
                print(f"ERROR: Failed to render LoginView: {e}")
        
        # Home Route (Field Worker)
        elif current_route == "/home":
            print("DEBUG: Rendering Home View")
                print(f"DEBUG: No user ID, redirecting to /login")
                page.go("/login")
                return
            
            try:
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
            except Exception as e:
                print(f"ERROR: Failed to render HomeView: {e}")

        # Requests Route
        elif current_route == "/requests":
            print("DEBUG: Rendering Requests View")
            if not state.user_id:
                page.go("/login")
                return

            try:
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
            except Exception as e:
                print(f"ERROR: Failed to render RequestsForm: {e}")

        # Admin Route
        elif current_route == "/admin":
            print("DEBUG: Rendering Admin View")
            if not state.user_id or state.user_role != "管理":
                page.go("/login")
                return

            try:
                page.views.append(
                    ft.View(
                        "/admin",
                        [
                            AdminDashboard(
                                page, 
                                db, 
                                on_back=lambda _: logout()
                            )
                        ]
                    )
                )
            except Exception as e:
                print(f"ERROR: Failed to render AdminDashboard: {e}")
        
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
        page.go("/login")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Initialize by checking current route. 
    # If it is /, the handler will redirect to /login
    print(f"DEBUG: Startup route check: {page.route}")
    if page.route == "/" or page.route == "":
        page.go("/login")
    else:
        # If started with a deep link (unlikely here but good practice), force check
        route_change(page)

if __name__ == "__main__":
    ft.app(target=main)
