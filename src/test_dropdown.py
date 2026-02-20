"""
Flet 0.80.5 対応 Dropdownテスト
on_change → on_select に移行して動作確認
"""
import flet as ft

def main(page: ft.Page):
    page.title = "Dropdown テスト (Flet 0.80)"
    
    # テスト用テキストフィールド（表示/非表示切替対象）
    manual_input = ft.TextField(
        label="手入力フィールド", 
        visible=False,
        multiline=True
    )
    
    status_text = ft.Text("ここに状態が表示されます", size=14, color="grey")
    
    # --- テスト1: on_select でイベント取得 ---
    def on_dropdown_select(e):
        # Flet 0.80ではe.dataに選択値が入る
        val = e.data if hasattr(e, 'data') else e.control.value
        status_text.value = f"選択された値: {val}"
        print(f"DEBUG: on_dropdown_select fired. e.data={e.data}, control.value={e.control.value}")
        
        if val == "その他":
            manual_input.visible = True
        else:
            manual_input.visible = False
            manual_input.value = ""
        
        page.update()
    
    dropdown = ft.Dropdown(
        label="テスト項目",
        options=[
            ft.dropdown.Option("項目A"),
            ft.dropdown.Option("項目B"),
            ft.dropdown.Option("その他"),
        ],
        on_select=on_dropdown_select,
        width=300,
    )
    
    # --- テスト2: サブカテゴリの動的更新テスト ---
    sub_dropdown = ft.Dropdown(
        label="サブカテゴリ",
        options=[],
        width=300,
    )
    
    categories = {
        "勤怠": ["有給休暇", "欠勤", "遅刻"],
        "金銭": ["交通費", "消耗品費", "会議費"],
        "その他": ["相談", "報告"],
    }
    
    def on_main_select(e):
        val = e.data if hasattr(e, 'data') else e.control.value
        print(f"DEBUG: on_main_select fired. val={val}")
        subs = categories.get(val, [])
        sub_dropdown.options = [ft.dropdown.Option(s) for s in subs]
        sub_dropdown.value = subs[0] if subs else None
        status_text.value = f"メインカテゴリ: {val} → サブ: {subs}"
        page.update()
    
    main_dropdown = ft.Dropdown(
        label="メインカテゴリ",
        options=[
            ft.dropdown.Option("勤怠"),
            ft.dropdown.Option("金銭"),
            ft.dropdown.Option("その他"),
        ],
        value="勤怠",
        on_select=on_main_select,
        width=300,
    )
    
    # 初期サブカテゴリ設定
    init_subs = categories["勤怠"]
    sub_dropdown.options = [ft.dropdown.Option(s) for s in init_subs]
    sub_dropdown.value = init_subs[0]
    
    page.add(
        ft.Text("=== Dropdown on_select テスト (Flet 0.80) ===", size=20, weight="bold"),
        ft.Container(height=20),
        ft.Text("テスト1: その他を選ぶと入力ボックスが出る", weight="bold"),
        dropdown,
        manual_input,
        ft.Container(height=20),
        ft.Text("テスト2: メインカテゴリでサブが変わる", weight="bold"),
        main_dropdown,
        sub_dropdown,
        ft.Container(height=20),
        status_text,
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
