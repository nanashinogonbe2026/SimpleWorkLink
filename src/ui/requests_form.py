import flet as ft
from database import Database

def RequestsForm(page: ft.Page, db: Database, user_id: int, on_back):
    
    # State for dynamic form fields
    category_dropdown = ft.Dropdown(
        label="申請種別",
        options=[
            ft.dropdown.Option("有給"),
            ft.dropdown.Option("休日"),
            ft.dropdown.Option("経費"),
            ft.dropdown.Option("部材"),
        ],
        value="有給",
    )
    category_dropdown.on_change = lambda e: update_form_visibility()

    reason_shortcuts = ft.Dropdown(
        label="定型理由（選択で入力）",
        options=[
            ft.dropdown.Option("私用のため"),
            ft.dropdown.Option("病院への通院"),
            ft.dropdown.Option("交通機関の遅延"),
            ft.dropdown.Option("現場消耗品購入"),
            ft.dropdown.Option("コインパーキング代"),
        ],
    )
    reason_shortcuts.on_change = lambda e: set_reason_text(e.control.value)

    content_field = ft.TextField(label="内容/理由", multiline=True, min_lines=2)
    amount_field = ft.TextField(label="金額/個数", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    
    # --- FilePicker Logic ---
    # We need to ensure the file picker is added to the page overlay when this view is active.
    # Since we are using manual routing with page.clean(), we must add it each time.
    file_picker = ft.FilePicker()
    file_picker.on_result = lambda e: update_file_label(e)
    page.overlay.append(file_picker)

    def update_file_label(e: ft.FilePickerResultEvent):
        # ... logic ...
        if e.files:
            file_label.value = f"選択済: {e.files[0].name}"
        else:
            file_label.value = "ファイル未選択"
        page.update()

    # ... (Rest of the logic set_reason_text, update_form_visibility, submit_request) ...

    # We return a Container acting as the "Screen"
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back),
                        ft.Text("各種申請", size=25, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Divider(),
                ft.Container(height=20),
                ft.Column(
                    [
                        category_dropdown,
                        ft.Container(height=10),
                        reason_shortcuts,
                        ft.Container(height=10),
                        content_field,
                        ft.Container(height=10),
                        amount_container,
                        ft.Container(height=10),
                        file_upload_container,
                        ft.Container(height=30),
                        ft.ElevatedButton(
                            content=ft.Text("申請・送信"),
                            icon=ft.Icons.SEND,
                            width=300,
                            height=60,
                            bgcolor=ft.Colors.BLUE_700,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=submit_request
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                )
            ],
            expand=True
        ),
        expand=True, # Ensure the container takes full space
        padding=20
    )
