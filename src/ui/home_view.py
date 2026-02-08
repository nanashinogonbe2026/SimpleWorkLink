import flet as ft
from database import Database
import datetime
import time

def HomeView(page: ft.Page, db: Database, user_id: int, user_name: str, on_navigate_requests, on_logout):
    
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
        width=350,
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
            timestamp = db.add_record(user_id, action_type, location)
            
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

    # UI Components
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
        on_click=lambda _: on_navigate_requests()
    )

    add_log(f"ようこそ、{user_name}さん。")

    # --- Notification Logic ---
    def check_notifications():
        recent = db.check_unread_responses(user_id)
        if recent:
            # recent: [(category, status, rejection_reason), ...]
            items = []
            for r in recent:
                cat, status, reason = r
                icon = ft.Icons.CHECK_CIRCLE if status == "承認済" else ft.Icons.ERROR
                color = "green" if status == "承認済" else "red"
                text = f"申請「{cat}」が{status}されました。"
                if status == "却下" and reason:
                    text += f"\n理由: {reason}"
                
                items.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=color),
                        title=ft.Text(text),
                    )
                )
            
            dlg = ft.AlertDialog(
                title=ft.Text("申請結果のお知らせ"),
                content=ft.Column(items, tight=True, width=400),
                actions=[
                    ft.TextButton("確認", on_click=lambda e: page.close_dialog())
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Check notifications on load (using a small delay or direct call if page is ready)
    # Since this is a component returning a control, we can't easily trigger page.dialog immediately 
    # if it's not added to page yet. 
    # However, since we are doing manual routing in main.py (page.clean + page.add), 
    # the control is added immediately after return.
    # We can use a threading timer or just rely on the user interaction? 
    # Better: return a user control (class) or just append a specialized invisible control that triggers it?
    # Or just call it? calling it here might try to update page before this container is added.
    # Safe bet: Use a small timer or an invisible control with did_mount.
    # For prototype, let's try calling it but wrapping in a delayed checking function or 
    # appending a button that user clicks? No, user wants "Login when".
    # Let's try `page.run_task` or similar if available, or just `check_notifications()` 
    # but handle the fact that `page.dialog` might need page to be updated first.
    # Actually, `navigate` in `main.py` calls `page.add` then `page.update`. 
    # If we modify `main.py` to call a method on the view, that works. 
    # But `HomeView` returns a Container.
    # implementation hacks: 
    # We can use `did_mount` of a UserControl. But we are using functions returning Controls.
    # We will simply append the dialog opening to the page asynchronously or just try it.
    # Since `page` is passed, `page.dialog = ...` works, but `dlg.open=True` needs `page.update()`.
    # If we do it here, it might be overwritten by `main.py`'s `page.update()`.
    # Let's define it and return it as a part of the UI, maybe a "Check Notifications" button that is 
    # auto-triggered? No.
    # We will try to execute it.
    
    # We'll modify `main.py` to handle `on_mount` or similar, OR just hack it here.
    # Let's add a `ft.ProgressBar(visible=False)` that has `did_mount` equivalent? No.
    # We will just call it. It should work if we rely on `main.py` calling `page.update()` at the end.
    
    # Actually, `check_notifications` accesses `page`.
    # Let's try calling it immediately.
    check_notifications()

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("現場ホーム", size=20, weight="bold", color="white"),
                            ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: on_logout(), icon_color="white")
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.BLUE_700,
                    height=60,
                    padding=ft.padding.only(left=20, right=10)
                ),
                ft.Container(
                    content=ft.Column(
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
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True
                )
            ]
        ),
        expand=True
    )
