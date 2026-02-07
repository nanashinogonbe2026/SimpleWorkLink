import flet as ft
from database import Database
from ui.admin_dashboard import AdminDashboard
from ui.requests_form import RequestsForm
import datetime
import time

# Initialize Database
db = Database()

# Mock current user ID for prototype
CURRENT_USER_ID = 1 

def main(page: ft.Page):
    page.title = "Simple-Work-Link"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F4F8"
    
    # Responsive window size for testing
    page.window_width = 400
    page.window_height = 800

    # --- Log & Status Components ---
    log_list = ft.ListView(
        expand=True, 
        spacing=10, 
        padding=10, 
        auto_scroll=True,
        height=150
    )

    log_container = ft.Container(
        content=log_list,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        padding=10,
        margin=ft.margin.only(top=20, bottom=10),
        width=350,  # Slightly wider than buttons
        height=200
    )

    status_text = ft.Text("System Status: Ready", size=12, color=ft.Colors.GREY_700)

    def add_log(message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_list.controls.append(ft.Text(f"[{timestamp}] {message}", size=14))
        page.update()

    def get_location_mock():
        return "35.6895, 139.6917"

    def on_clock_action(e):
        action_type = e.control.data
        
        # Disable buttons and show processing status
        btn_clock_in.disabled = True
        btn_clock_out.disabled = True
        status_text.value = "System Status: Processing..."
        add_log(f"{action_type}処理を開始します...")
        page.update()

        # Simulate small delay for user feedback
        time.sleep(0.5)

        try:
            location = get_location_mock()
            timestamp = db.add_record(CURRENT_USER_ID, action_type, location)
            
            success_msg = f"{action_type}完了: {timestamp}"
            add_log(success_msg)
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text(success_msg, size=20, weight="bold"),
                bgcolor="green",
                duration=3000
            )
            page.snack_bar.open = True
            status_text.value = "System Status: Idle (Last Action Success)"
            
        except Exception as ex:
            error_msg = f"エラー発生: {str(ex)}"
            add_log(error_msg)
            status_text.value = "System Status: Error"
        
        finally:
            # Re-enable buttons
            btn_clock_in.disabled = False
            btn_clock_out.disabled = False
            page.update()

    # UI Components (Field) - Defined BEFORE logic that uses them
    BUTTON_STYLE = {
        "width": 300,
        "height": 180,
        "style": ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20))
    }

    btn_clock_in = ft.FilledButton(
        data="出勤",
        on_click=on_clock_action,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.WB_SUNNY, size=50, color=ft.Colors.WHITE),
                ft.Text("出勤", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        **BUTTON_STYLE
    )

    btn_clock_out = ft.FilledButton(
        data="退勤",
        on_click=on_clock_action,
        bgcolor=ft.Colors.ORANGE_800,
        color=ft.Colors.WHITE,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.NIGHTLIGHT_ROUND, size=50, color=ft.Colors.WHITE),
                ft.Text("退勤", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        **BUTTON_STYLE
    )

    btn_requests = ft.FilledButton(
        content=ft.Text("各種申請"),
        icon=ft.Icons.ASSIGNMENT,
        width=300,
        height=60,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        bgcolor=ft.Colors.GREY_300,
        color=ft.Colors.BLACK,
        on_click=lambda _: page.go("/requests")
    )

    # --- DEBUG: Direct Render Mode (Routing Disabled) ---
    # Navigation Logic - Commented out for debugging
    # def route_change(route):
    #     ...
    
    # page.on_route_change = route_change
    # page.on_view_pop = view_pop
    
    # page.go("/")

    # Directly add Home components to page
    page.appbar = ft.AppBar(
        title=ft.Text("現場用 (Debug Mode)"),
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        actions=[
            # ft.IconButton(ft.Icons.ADMIN_PANEL_SETTINGS, on_click=lambda _: page.go("/admin")) # Nav disabled
        ]
    )

    page.add(
        ft.Column(
            [
                ft.Container(height=20),
                btn_clock_in,
                ft.Container(height=30),
                btn_clock_out,
                ft.Container(height=30),
                btn_requests,
                log_container,
                status_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    
    add_log("アプリが起動しました。")
    page.update()
    print("DEBUG: Page updated with direct controls")

# Revert to ft.app(target=main) to ensure app stays open
ft.app(target=main)
