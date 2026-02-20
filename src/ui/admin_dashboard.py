import flet as ft
from database import Database
import datetime

def AdminDashboard(page: ft.Page, db: Database, on_back):
    # Mock Admin ID
    ADMIN_ID = 2 # Assuming admin is ID 2 based on default data, but in real app we should use actual logged in ID.

    # --- UI Components for Attendance Management ---
    def edit_record_dialog(record, refresh_callback):
        # record: (id, name, type, timestamp, status, location)
        record_id = record[0]
        current_time = record[3]
        current_status = record[4]

        time_field = ft.TextField(label="日時 (YYYY-MM-DD HH:MM:SS)", value=current_time)
        status_field = ft.Dropdown(
            label="ステータス",
            options=[
                ft.dropdown.Option("正常"),
                ft.dropdown.Option("修正済"),
                ft.dropdown.Option("無効"),
            ],
            value=current_status
        )

        def save_changes(e):
            success = db.update_record(record_id, time_field.value, status_field.value, ADMIN_ID)
            if success:
                page.snack_bar = ft.SnackBar(ft.Text("修正を保存しました"), bgcolor="green")
                dlg.open = False
                refresh_callback()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("保存に失敗しました"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("打刻修正"),
            content=ft.Column([
                ft.Text(f"対象: {record[1]} ({record[2]})"),
                time_field,
                status_field
            ], tight=True),
            actions=[
                ft.TextButton(content=ft.Text("キャンセル"), on_click=lambda e: page.close_dialog()),
                ft.TextButton(content=ft.Text("保存"), on_click=save_changes),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def get_attendance_content():
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("日時")),
                ft.DataColumn(ft.Text("氏名")),
                ft.DataColumn(ft.Text("種別")),
                ft.DataColumn(ft.Text("状態")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[],
        )

        def refresh_table():
            records = db.get_all_records()
            rows = []
            for r in records:
                # r: (id, name, type, timestamp, status, location)
                is_late = False
                if r[2] == "出勤":
                    try:
                        dt = datetime.datetime.strptime(r[3], "%Y-%m-%d %H:%M:%S")
                        if dt.time() > datetime.time(9, 15):
                            is_late = True
                    except ValueError:
                        pass

                cell_style = ft.TextStyle(color=ft.Colors.RED, weight=ft.FontWeight.BOLD) if is_late else None
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(r[3], style=cell_style)), # Time
                            ft.DataCell(ft.Text(r[1], style=cell_style)), # Name
                            ft.DataCell(ft.Text(r[2], style=cell_style)), # Type
                            ft.DataCell(ft.Text(r[4], style=cell_style)), # Status
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=ft.Colors.BLUE,
                                    on_click=lambda e, rec=r: edit_record_dialog(rec, refresh_table)
                                )
                            ),
                        ],
                    )
                )
            data_table.rows = rows
            page.update()

        refresh_table()

        return ft.Column([
            ft.Row([
                ft.Text("打刻一覧 (9:15以降は赤字)", size=16, color="grey"),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: refresh_table())
            ]),
            ft.Column([data_table], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True)

    # --- UI Components for User Management ---
    
    def add_user_dialog(refresh_callback):
        name_field = ft.TextField(label="氏名")
        role_field = ft.Dropdown(
            label="権限ロール",
            options=[ft.dropdown.Option("現場"), ft.dropdown.Option("管理")],
            value="現場"
        )
        login_id_field = ft.TextField(label="ログインID (半角英数)")
        password_field = ft.TextField(label="パスワード", password=True, can_reveal_password=True)
        
        error_text = ft.Text("", color="red")

        def save_user(e):
            if not all([name_field.value, role_field.value, login_id_field.value, password_field.value]):
                error_text.value = "全ての項目を入力してください"
                page.update()
                return

            success, msg = db.add_user(name_field.value, role_field.value, login_id_field.value, password_field.value)
            if success:
                page.snack_bar = ft.SnackBar(ft.Text("ユーザーを追加しました"), bgcolor="green")
                dlg.open = False
                refresh_callback()
            else:
                error_text.value = msg
            
            page.snack_bar.open = True
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("新規ユーザー登録"),
            content=ft.Column([
                name_field,
                role_field,
                login_id_field,
                password_field,
                error_text
            ], tight=True, width=400),
            actions=[
                ft.TextButton("キャンセル", on_click=lambda e: page.close_dialog()),
                ft.TextButton("登録", on_click=save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def get_user_management_content():
        user_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("氏名")),
                ft.DataColumn(ft.Text("ロール")),
                ft.DataColumn(ft.Text("ログインID")),
                ft.DataColumn(ft.Text("状態")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[]
        )

        def toggle_user_active(user_id, current_active):
            new_active = not current_active
            db.toggle_user_active(user_id, new_active)
            refresh_users()
            page.snack_bar = ft.SnackBar(ft.Text(f"ユーザーID {user_id} の状態を変更しました"), bgcolor="green")
            page.snack_bar.open = True
            page.update()

        def refresh_users():
            users = db.get_all_users()
            rows = []
            for u in users:
                # u: (id, name, role, login_id, is_active)
                uid, name, role, lid, is_active = u
                
                status_text = "有効" if is_active else "無効"
                status_color = ft.Colors.GREEN if is_active else ft.Colors.RED
                
                action_icon = ft.Icons.BLOCK if is_active else ft.Icons.CHECK_CIRCLE
                action_color = ft.Colors.RED if is_active else ft.Colors.GREEN
                action_tooltip = "無効化" if is_active else "有効化"

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(uid))),
                            ft.DataCell(ft.Text(name)),
                            ft.DataCell(ft.Text(role)),
                            ft.DataCell(ft.Text(lid)),
                            ft.DataCell(ft.Text(status_text, color=status_color, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(
                                ft.IconButton(
                                    icon=action_icon,
                                    icon_color=action_color,
                                    tooltip=action_tooltip,
                                    on_click=lambda e, u_id=uid, active=is_active: toggle_user_active(u_id, active)
                                )
                            ),
                        ]
                    )
                )
            user_table.rows = rows
            page.update()

        refresh_users()

        return ft.Column([
            ft.Row([
                ft.Text("ユーザー一覧", size=16, weight="bold"),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "新規ユーザー追加", 
                    icon=ft.Icons.PERSON_ADD, 
                    on_click=lambda _: add_user_dialog(refresh_users)
                )
            ]),
            ft.Column([user_table], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True)

    # --- Main Layout with Tabs ---
    
    def get_requests_content():
        # Using closure state for the modal logic
        
        current_req_id = [None] # Mutable ref to store current processing ID
        
        # --- Custom Modal Components ---
        reject_template_dropdown = ft.Dropdown(
            label="却下理由（定型文）",
            options=[
                ft.dropdown.Option("入力不備"),
                ft.dropdown.Option("領収書不足"),
                ft.dropdown.Option("金額不整合"),
                ft.dropdown.Option("その他"),
            ],
            width=300,
        )
        
        reject_reason_field = ft.TextField(
            label="詳細理由（必須）",
            multiline=True,
            width=300,
            visible=False
        )

        reject_dialog_container = ft.Container(visible=False, expand=True)

        def set_reject_template(val):
            # 却下理由テンプレートの選択に応じて手書き入力欄の表示を切替
            print(f"DEBUG: set_reject_template called. Value: {val}")
            if val == "その他":
                reject_reason_field.visible = True
            else:
                reject_reason_field.visible = False
                reject_reason_field.value = ""
            
            print(f"DEBUG: reject_reason_field.visible = {reject_reason_field.visible}")
            # ネストされたStack/Container内でも確実にUIを更新
            page.update()

        # Bind event handler
        # Flet 0.80: on_change → on_select に変更
        reject_template_dropdown.on_select = lambda e: set_reject_template(e.data)

        def close_reject_dialog():
            print("DEBUG: close_reject_dialog called")
            reject_dialog_container.visible = False
            reject_reason_field.value = ""
            reject_template_dropdown.value = ""
            reject_dialog_container.update()
            page.update()

        def confirm_rejection(e):
            print("DEBUG: confirm_rejection called")
            # ... (rest of logic)
            if current_req_id[0] is not None:
                reason = reject_template_dropdown.value
                
                if not reason:
                     page.snack_bar = ft.SnackBar(ft.Text("却下理由を選択してください"), bgcolor="red")
                     page.snack_bar.open = True
                     page.update()
                     return

                if reason == "その他":
                    reason = reject_reason_field.value
                    if not reason:
                        page.snack_bar = ft.SnackBar(ft.Text("理由を入力してください"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                        return
                
                db.update_request_status(current_req_id[0], "却下", reason)
                refresh_requests() # Update table
                page.snack_bar = ft.SnackBar(ft.Text("申請を却下しました"), bgcolor="grey")
                page.snack_bar.open = True
                page.update()
                close_reject_dialog()

        # Custom Modal Content UI
        modal_content = ft.Container(
            content=ft.Column([
                ft.Text("却下理由の入力", size=18, weight="bold"),
                ft.Container(height=10),
                reject_template_dropdown,
                reject_reason_field,
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("キャンセル", on_click=lambda _: close_reject_dialog()),
                    ft.ElevatedButton("却下確定", on_click=confirm_rejection, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.END)
            ]), 
            width=400, 
            bgcolor=ft.Colors.WHITE, 
            padding=20, 
            border_radius=10,
            alignment=ft.Alignment(0, 0),
        )

        overlay_bg = ft.Container(
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
            on_click=lambda _: close_reject_dialog(),
        )

        reject_dialog_container.content = ft.Stack([
            overlay_bg,
            modal_content
        ], expand=True)

        def open_reject_dialog(req_id):
            # 却下ダイアログを開く（状態をリセットしてから表示）
            current_req_id[0] = req_id
            reject_reason_field.value = ""
            reject_reason_field.visible = False
            reject_template_dropdown.value = None
            
            reject_dialog_container.visible = True
            page.update()

        # Requests Table Logic
        requests_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("日時")),
                ft.DataColumn(ft.Text("氏名")),
                ft.DataColumn(ft.Text("種別")),
                ft.DataColumn(ft.Text("内容")),
                ft.DataColumn(ft.Text("金額")),
                ft.DataColumn(ft.Text("状態")),
                ft.DataColumn(ft.Text("理由/備考")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[]
        )

        def update_status(req_id, new_status):
            # This function is now only for "承認済"
            db.update_request_status(req_id, new_status)
            refresh_requests()
            page.snack_bar = ft.SnackBar(ft.Text(f"申請を{new_status}しました"), bgcolor="green")
            page.snack_bar.open = True
            page.update()

        def refresh_requests():
            requests = db.get_all_requests()
            rows = []
            for r in requests:
                rid, rname, rcat, rcontent, ramount, rstatus, rtime, rreason = r
                
                status_color = ft.Colors.BLACK
                if rstatus == "承認済": status_color = ft.Colors.GREEN
                elif rstatus == "却下": status_color = ft.Colors.RED
                elif rstatus == "未承認": status_color = ft.Colors.ORANGE

                actions = [
                    ft.IconButton(ft.Icons.CHECK, icon_color="green", tooltip="承認", on_click=lambda e, i=rid: update_status(i, "承認済")),
                    ft.IconButton(ft.Icons.CLOSE, icon_color="red", tooltip="却下", on_click=lambda e, i=rid: open_reject_dialog(i))
                ]

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(rtime)),
                            ft.DataCell(ft.Text(rname)),
                            ft.DataCell(ft.Text(rcat)),
                            ft.DataCell(ft.Text(rcontent, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, width=150)),
                            ft.DataCell(ft.Text(str(ramount) if ramount else "-")),
                            ft.DataCell(ft.Text(rstatus, color=status_color, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(rreason if rreason else "-", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, width=100)),
                            ft.DataCell(ft.Row(actions, spacing=0)),
                        ]
                    )
                )
            requests_table.rows = rows
            # Safe update
            try:
                if requests_table.page:
                    requests_table.update()
            except Exception:
                pass # Control might not be on page yet

        refresh_requests()

        main_content = ft.Column([
            ft.Row([
                ft.Text("申請一覧", size=16, weight="bold"),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: refresh_requests())
            ]),
            ft.Column([requests_table], scroll=ft.ScrollMode.AUTO, expand=True) 
        ], expand=True)

        return ft.Stack([
            main_content,
            reject_dialog_container
        ], expand=True)

    # --- Manual Tab Implementation ---
    content_area = ft.Container(expand=True, padding=20)

    def show_tab(tab_name):
        # Update tab styling
        btn_attendance.style = ft.ButtonStyle(color=ft.Colors.BLUE if tab_name == "attendance" else ft.Colors.GREY)
        btn_users.style = ft.ButtonStyle(color=ft.Colors.BLUE if tab_name == "users" else ft.Colors.GREY)
        btn_requests.style = ft.ButtonStyle(color=ft.Colors.BLUE if tab_name == "requests" else ft.Colors.GREY)
        
        # Update content
        if tab_name == "attendance":
            content_area.content = get_attendance_content()
        elif tab_name == "users":
            content_area.content = get_user_management_content()
        elif tab_name == "requests":
            content_area.content = get_requests_content()
        
        page.update()

    btn_attendance = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.ACCESS_TIME), ft.Text("勤怠管理")]),
        on_click=lambda _: show_tab("attendance")
    )
    
    btn_users = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.PEOPLE), ft.Text("ユーザー管理")]),
        on_click=lambda _: show_tab("users")
    )

    btn_requests = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.ASSIGNMENT), ft.Text("申請管理")]),
        on_click=lambda _: show_tab("requests")
    )

    # Initial Loading
    content_area.content = get_attendance_content()
    btn_attendance.style = ft.ButtonStyle(color=ft.Colors.BLUE)
    btn_users.style = ft.ButtonStyle(color=ft.Colors.GREY)
    btn_requests.style = ft.ButtonStyle(color=ft.Colors.GREY)

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back),
                        ft.Text("管理ダッシュボード", size=25, weight="bold"),
                        ft.Container(expand=True),
                        ft.Text(f"Admin ID: {ADMIN_ID}", color="grey")
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Divider(),
                ft.Row([btn_attendance, btn_users, btn_requests], alignment=ft.MainAxisAlignment.START),
                ft.Divider(),
                content_area
            ],
            expand=True
        ),
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE
    )
