import flet as ft

class GlassCard(ft.Container):
    def __init__(self, content, width=None, height=None, on_click=None, padding=20):
        super().__init__(
            content=content,
            width=width,
            height=height,
            border_radius=15,
            padding=padding,
            # Default State
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
            ),
            on_click=on_click,
            on_hover=self.handle_hover, # <--- Connect the hover event
            animate=ft.animation.Animation(200, "easeOut"), # Smooth transition
            animate_scale=ft.animation.Animation(200, "easeOut"),
        )

    def handle_hover(self, e):
        if e.data == "true": # Mouse Enter
            self.bgcolor = ft.colors.with_opacity(0.1, "#6200EA") # Purple tint
            self.border = ft.border.all(1, ft.colors.with_opacity(0.5, "#BB86FC")) # Glow border
            self.shadow.blur_radius = 20
            self.shadow.color = ft.colors.with_opacity(0.4, "#6200EA") # Purple shadow
            self.scale = 1.02 # Slight lift
        else: # Mouse Exit
            self.bgcolor = ft.colors.with_opacity(0.05, ft.colors.WHITE)
            self.border = ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE))
            self.shadow.blur_radius = 10
            self.shadow.color = ft.colors.with_opacity(0.1, ft.colors.BLACK)
            self.scale = 1.0
        self.update()