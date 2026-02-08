import flet as ft
import inspect

print(f"Flet version: {ft.version}")
try:
    print(f"Tab init signature: {inspect.signature(ft.Tab.__init__)}")
except Exception as e:
    print(f"Error: {e}")

print("Tab attributes: ", dir(ft.Tab))
