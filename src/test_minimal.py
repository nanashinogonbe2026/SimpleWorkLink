import flet as ft

def main(page: ft.Page):
    print("DEBUG: Minimal app starting")
    page.add(
        ft.Text("もしこれが見えたら、Fletは正常です。", size=30, color="blue", weight="bold"),
        ft.ElevatedButton("押せますか？", on_click=lambda e: print("Button clicked"))
    )
    print("DEBUG: Controls added, updating page")
    page.update()

if __name__ == "__main__":
    print("DEBUG: Calling ft.app")
    try:
        # Try the older compatible method first since run() gave issues
        ft.app(target=main)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
