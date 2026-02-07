import flet as ft

def LoginView(page: ft.Page, on_login):
    """
    簡易ログイン画面
    on_login: (user_id, role) -> None
    """
    
    def handle_login(e, user_id, role):
        on_login(user_id, role)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Simple-Work-Link", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("ログインユーザーを選択してください（プロトタイプ）", size=16, color=ft.Colors.GREY_700),
                ft.Container(height=50),
                
                # User 1: Field Worker
                ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ENGINEERING, size=40),
                            ft.Text("山田 太郎 (現場)", size=20)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=20,
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.WHITE,
                        color=ft.Colors.BLUE_700,
                        elevation=5
                    ),
                    width=250,
                    height=120,
                    on_click=lambda e: handle_login(e, 1, "現場")
                ),
                
                ft.Container(height=30),

                # User 2: Admin
                ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=40),
                            ft.Text("鈴木 一郎 (管理)", size=20)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=20,
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.GREY_800,
                        color=ft.Colors.WHITE,
                        elevation=5
                    ),
                    width=250,
                    height=120,
                    on_click=lambda e: handle_login(e, 2, "管理")
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=ft.Colors.BLUE_50
    )
