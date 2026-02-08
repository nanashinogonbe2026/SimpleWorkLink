import flet as ft
import inspect

print(f"Flet version: {ft.version}")
print("ft.Tab constructor:")
try:
    print(inspect.signature(ft.Tab))
except Exception as e:
    print(f"Could not get signature: {e}")

print("\nft.Tab help:")
help(ft.Tab)
