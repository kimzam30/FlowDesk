import flet as ft

def get_ambient_background(page_width, page_height):
    return ft.Stack(
        controls=[
            # Deep Black Background
            ft.Container(
                expand=True, 
                bgcolor="#050505" # OLED Black
            ),
            # Purple Glow (Top Left)
            ft.Container(
                width=400,
                height=400,
                left=-100,
                top=-100,
                gradient=ft.RadialGradient(
                    colors=[ft.colors.with_opacity(0.3, "#6200EA"), "transparent"],
                ),
            ),
            # Indigo Glow (Bottom Right)
            ft.Container(
                width=500,
                height=500,
                right=-150,
                bottom=-150,
                gradient=ft.RadialGradient(
                    colors=[ft.colors.with_opacity(0.2, "#304FFE"), "transparent"],
                ),
            ),
        ]
    )