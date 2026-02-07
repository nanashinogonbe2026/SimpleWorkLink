import flet as ft
from database import Database
import datetime

def AdminDashboard(page: ft.Page, db: Database, on_back):
    # Mock Admin ID
    ADMIN_ID = 2

    def edit_record_dialog(record):
        # record: (id, name, type, timestamp, status, location)
        
        record_id = record[0]
        current_time = record[3]
        current_status = record[4]

        time_field = ft.TextField(label="日時", value=current_time)
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
                refresh_table()
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

    def get_data_rows():
        records = db.get_all_records()
        rows = []
        for r in records:
            # r: (id, name, type, timestamp, status, location)
            # Alert Logic: Mark as red if clock-in is after 09:15
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
                                on_click=lambda e, rec=r: edit_record_dialog(rec)
                            )
                        ),
                    ],
                )
            )
        return rows

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
        data_table.rows = get_data_rows()
        page.update()

    refresh_table()

    # --- New Features Logic ---
    # ... (Previous logic for data table, dialogs, etc.) ...
    
    # FilePicker for CSV
    csv_picker = ft.FilePicker()
    csv_picker.on_result = lambda e: save_csv(e)
    page.overlay.append(csv_picker)

    def save_csv(e: ft.FilePickerResultEvent):
        # ... (CSV logic) ...
        pass # Logic handled below

    # Check for risk alerts
    alert_container = get_risk_alert()

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back),
                        ft.Text("管理ダッシュボード", size=25, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            content=ft.Text("CSV出力"), 
                            icon=ft.Icons.DOWNLOAD, 
                            on_click=lambda _: csv_picker.save_file(allowed_extensions=["csv"], file_name="monthly_report.csv")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Divider(),
                alert_container,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("打刻一覧 (9:15以降は赤字)", size=16, color=ft.Colors.GREY),
                            data_table
                        ],
                        scroll=ft.ScrollMode.AUTO
                    ),
                    expand=True
                )
            ],
            expand=True
        ),
        expand=True,
        padding=20
    )
