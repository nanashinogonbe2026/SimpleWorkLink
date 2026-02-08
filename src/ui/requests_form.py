import flet as ft
from database import Database

class RequestsFormController:
    def __init__(self, page: ft.Page, db: Database, user_id: int, on_back):
        self.page = page
        self.db = db
        self.user_id = user_id
        self.on_back = on_back
        
        # --- Data Definitions ---
        self.CATEGORY_DATA = {
            "勤怠": {
                "subs": ["有給休暇", "欠勤", "遅刻", "早退", "休日出勤", "振替休日"],
                "reasons": ["私用のため", "体調不良", "通院", "公的機関の手続き", "交通機関の遅延", "その他"]
            },
            "金銭": {
                "subs": ["交通費", "消耗品費", "会議費", "部材購入", "仮払い"],
                "reasons": ["電車・バス利用", "タクシー利用", "現場備品購入", "接待・会食", "その他"]
            },
            "その他": {
                "subs": ["相談", "報告", "トラブル報告", "その他"],
                "reasons": ["その他"]
            }
        }
        
        # --- UI Components ---
        self.main_category = ft.Dropdown(
            label="申請区分",
            options=[
                ft.dropdown.Option("勤怠"),
                ft.dropdown.Option("金銭"),
                ft.dropdown.Option("その他"),
            ],
            value="勤怠",
        )

        self.sub_category = ft.Dropdown(
            label="詳細種別",
            options=[],
            value=""
        )

        self.reason_template = ft.Dropdown(
            label="理由・内容（選択）",
            options=[],
            value="",
        )

        self.content_manual = ft.TextField(
            label="理由・内容（詳細手入力）", 
            multiline=True, 
            min_lines=2, 
            visible=False
        )
        
        self.amount_field = ft.TextField(
            label="金額/個数", 
            value="0", 
            keyboard_type=ft.KeyboardType.NUMBER
        )
        self.amount_container = ft.Container(content=self.amount_field, visible=False)
        
        self.file_label = ft.Text("ファイル機能は現在無効です")
        self.file_upload_container = ft.Container(
            content=ft.Row([
                ft.ElevatedButton("領収書/写真添付", icon=ft.Icons.CAMERA_ALT, on_click=lambda _: print("Disabled")),
                self.file_label
            ]),
            visible=False
        )

        self.content_area = ft.Container(padding=10)
        
        self.btn_new = ft.TextButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE), ft.Text("新規申請")]),
            on_click=lambda _: self.show_tab("new"),
            style=ft.ButtonStyle(color=ft.Colors.BLUE)
        )
        
        self.btn_history = ft.TextButton(
            content=ft.Row([ft.Icon(ft.Icons.HISTORY), ft.Text("履歴")]),
            on_click=lambda _: self.show_tab("history"),
            style=ft.ButtonStyle(color=ft.Colors.GREY)
        )

        # --- Bind Events (after components are defined) ---
        self.main_category.on_change = self.on_main_category_change
        self.reason_template.on_change = self.on_reason_template_change

        # Initialize Logic
        self.initialize_state()

    def initialize_state(self):
        # Initial populate based on default main_category value
        init_cat = self.main_category.value
        init_data = self.CATEGORY_DATA.get(init_cat, {})
        
        self.sub_category.options = [ft.dropdown.Option(s) for s in init_data.get("subs", [])]
        self.sub_category.value = init_data.get("subs", [])[0] if init_data.get("subs") else None
        
        self.reason_template.options = [ft.dropdown.Option(r) for r in init_data.get("reasons", ["その他"])]
        self.reason_template.value = init_data.get("reasons", ["その他"])[0] if init_data.get("reasons") else None
        
        self.content_manual.visible = (self.reason_template.value == "その他")
        
        # Set visibility for amount/file based on initial category
        is_money = (init_cat == "金銭")
        self.amount_container.visible = is_money
        self.file_upload_container.visible = is_money

        # Open Default Tab
        self.show_tab("new", update_ui=False)

    def on_main_category_change(self, e):
        print(f"DEBUG: on_main_category_change. Value: {self.main_category.value}")
        self.update_options_logic()
        self.page.update()

    def on_reason_template_change(self, e):
        print(f"DEBUG: on_reason_template_change. Value: {self.reason_template.value}")
        self.check_manual_reason_visibility()
        self.page.update()

    def update_options_logic(self):
        cat = self.main_category.value
        data = self.CATEGORY_DATA.get(cat, {})
        
        # Update Sub Categories
        subs = data.get("subs", [])
        self.sub_category.options = [ft.dropdown.Option(s) for s in subs]
        if not self.sub_category.value or self.sub_category.value not in subs:
            self.sub_category.value = subs[0] if subs else None
            
        # Update Reasons
        reasons = data.get("reasons", ["その他"])
        self.reason_template.options = [ft.dropdown.Option(r) for r in reasons]
        if not self.reason_template.value or self.reason_template.value not in reasons:
            self.reason_template.value = reasons[0] if reasons else None
            
        # Update Visibility
        is_money = (cat == "金銭")
        self.amount_container.visible = is_money
        self.file_upload_container.visible = is_money
        
        self.check_manual_reason_visibility(update_ui=False) # Don't update page here, parent will

        # Explicit Updates for affected controls
        self.sub_category.update()
        self.reason_template.update()
        self.amount_container.update()
        self.file_upload_container.update()
        self.content_manual.update()

    def check_manual_reason_visibility(self, update_ui=True):
        if self.reason_template.value == "その他":
            self.content_manual.visible = True
        else:
            self.content_manual.visible = False
        
        if update_ui:
            self.content_manual.update()

    def submit_request(self, e):
        main = self.main_category.value
        sub = self.sub_category.value
        cat_str = f"{main} - {sub}"
        
        reason = self.reason_template.value
        if reason == "その他":
            manual_text = self.content_manual.value
            if not manual_text:
                self.page.snack_bar = ft.SnackBar(ft.Text("詳細理由を入力してください"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()
                return
            content_str = manual_text
        else:
            content_str = reason

        amount = 0.0
        if self.amount_container.visible:
            try:
                amount = float(self.amount_field.value)
            except ValueError:
                self.page.snack_bar = ft.SnackBar(ft.Text("金額は数値で入力してください"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()
                return

        success = self.db.add_request(self.user_id, cat_str, content_str, amount)
        if success:
            self.page.snack_bar = ft.SnackBar(ft.Text("申請が完了しました"), bgcolor="green")
            self.page.snack_bar.open = True
            self.show_tab("history")
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("申請に失敗しました"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def show_tab(self, tab_name, update_ui=True):
        self.btn_new.style = ft.ButtonStyle(color=ft.Colors.BLUE if tab_name == "new" else ft.Colors.GREY)
        self.btn_history.style = ft.ButtonStyle(color=ft.Colors.BLUE if tab_name == "history" else ft.Colors.GREY)

        if tab_name == "new":
            self.content_area.content = self.get_application_form_content()
        elif tab_name == "history":
            self.content_area.content = self.get_history_view_content()
        
        if update_ui:
            self.content_area.update()
            self.btn_new.update()
            self.btn_history.update()

    def get_application_form_content(self):
        return ft.Column(
            [
                ft.Text("新規申請", size=18, weight="bold"),
                ft.Container(height=10),
                self.main_category,
                self.sub_category,
                ft.Container(height=10),
                self.reason_template,
                self.content_manual,
                ft.Container(height=10),
                self.amount_container,
                ft.Container(height=10),
                self.file_upload_container,
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text("申請・送信"),
                    icon=ft.Icons.SEND,
                    width=300,
                    height=60,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=self.submit_request
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def get_history_view_content(self):
        requests = self.db.get_user_requests(self.user_id)
        items = []
        for r in requests:
            rid, cat, content, amount, status, timestamp, reason = r
            
            icon = ft.Icons.CIRCLE
            color = ft.Colors.GREY
            if status == "承認済":
                icon = ft.Icons.CHECK_CIRCLE
                color = ft.Colors.GREEN
            elif status == "却下":
                icon = ft.Icons.ERROR
                color = ft.Colors.RED
            elif status == "未承認":
                icon = ft.Icons.HOURGLASS_EMPTY
                color = ft.Colors.ORANGE

            details = [ft.Text(f"内容: {content}")]
            if amount:
                details.append(ft.Text(f"金額: {amount}"))
            if status == "却下" and reason:
                details.append(ft.Text(f"却下理由: {reason}", color=ft.Colors.RED, weight="bold"))

            items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon, color=color),
                            ft.Text(cat, weight="bold", size=16),
                            ft.Container(expand=True),
                            ft.Text(timestamp, size=12, color="grey")
                        ]),
                        ft.Container(
                            content=ft.Column(details),
                            padding=ft.padding.only(left=30)
                        ),
                        ft.Text(f"ステータス: {status}", color=color, size=12, weight="bold", text_align=ft.TextAlign.RIGHT)
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                    bgcolor=ft.Colors.WHITE
                )
            )

        if not items:
            items.append(ft.Text("申請履歴はありません"))

        return ft.Column(
            [
                ft.Row([
                   ft.Text("申請履歴", size=18, weight="bold"),
                   ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: self.show_tab("history")) 
                ]),
                ft.ListView(controls=items, expand=True, spacing=10)
            ],
            expand=True
        )

    def get_view(self):
        return ft.Column([
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.on_back),
                    ft.Text("各種申請", size=25, weight="bold"),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.Divider(),
            ft.Row([self.btn_new, self.btn_history], alignment=ft.MainAxisAlignment.CENTER),
            self.content_area
        ], expand=True, scroll=ft.ScrollMode.AUTO)

# Helper for main.py compatibility
def RequestsFormView(page: ft.Page, db: Database, user_id: int, on_back):
    controller = RequestsFormController(page, db, user_id, on_back)
    # Important: Return the VIEW (Control), but the controller must trigger updates.
    # Since we are not using UserControl, the controller instance might be lost if not stored.
    # BUT, the controls (Dropdown etc.) are bound to the controller's methods.
    # Bound methods hold references to `self` (the controller).
    # So the controller should be kept alive by the UI controls themselves.
    return controller.get_view()
