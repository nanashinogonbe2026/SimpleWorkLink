import flet as ft
import inspect

print(f"Flet version: {ft.version}")

try:
    print("\n--- ft.Tab signature ---")
    print(inspect.signature(ft.Tab.__init__))
except Exception as e:
    print(f"Tab sig error: {e}")

try:
    print("\n--- ft.Tabs signature ---")
    print(inspect.signature(ft.Tabs.__init__))
except Exception as e:
    print(f"Tabs sig error: {e}")

print("\n--- ft.Tab dir ---")
print([d for d in dir(ft.Tab) if not d.startswith("_")])
