import flet as ft
import time
import threading
from src.ui.components.glass_card import GlassCard

class FocusMode(ft.UserControl):
    def __init__(self, page, task_title, on_exit, on_complete):
        super().__init__()
        self.page = page
        self.task_title = task_title
        self.on_exit = on_exit
        self.on_complete = on_complete
        
        # Timer Config
        self.total_seconds = 25 * 60
        self.current_seconds = self.total_seconds
        self.timer_running = False
        
        # Audio Players
        self.audio_rain = ft.Audio(src="assets/sounds/rain.mp3", autoplay=False, release_mode="loop")
        self.audio_wind = ft.Audio(src="assets/sounds/wind.mp3", autoplay=False, release_mode="loop")
        self.audio_thunder = ft.Audio(src="assets/sounds/thunder.mp3", autoplay=False, release_mode="loop")
        self.page.overlay.extend([self.audio_rain, self.audio_wind, self.audio_thunder])

        # --- UI COMPONENTS ---
        
        # 1. The Timer Text (Clickable)
        self.timer_text = ft.Text(
            "25:00", 
            size=100, 
            weight="bold", 
            color="white", 
            font_family="monospace"
        )
        self.timer_container = ft.GestureDetector(
            on_tap=self.open_edit_time_dialog,
            content=self.timer_text
        )

        # 2. Play Button
        self.play_icon = ft.IconButton(
            ft.icons.PLAY_ARROW_ROUNDED, 
            icon_size=40, 
            icon_color="white", 
            bgcolor=ft.colors.with_opacity(0.2, "white"),
            on_click=self.toggle_timer
        )

        # 3. Mode Pills (Pomodoro / Short / Long)
        self.mode_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.create_mode_button("Pomodoro", 25),
                self.create_mode_button("Short Break", 5),
                self.create_mode_button("Long Break", 15),
            ]
        )

    def create_mode_button(self, label, mins):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border_radius=20,
            bgcolor=ft.colors.with_opacity(0.2, "black"),
            on_click=lambda e: self.set_time_direct(mins),
            content=ft.Text(label, size=12, color="white")
        )

    def set_time_direct(self, minutes):
        self.timer_running = False
        self.play_icon.icon = ft.icons.PLAY_ARROW_ROUNDED
        self.total_seconds = minutes * 60
        self.current_seconds = self.total_seconds
        self.timer_text.value = "{:02d}:00".format(minutes)
        self.update()

    def open_edit_time_dialog(self, e):
        if self.timer_running: return

        # Input field for custom time
        time_input = ft.TextField(
            label="Minutes", 
            value=str(self.total_seconds // 60), 
            autofocus=True, 
            text_align="center"
        )

        def save_time(e):
            try:
                mins = int(time_input.value)
                self.set_time_direct(mins)
                self.page.dialog.open = False
                self.page.update()
            except ValueError:
                pass # Ignore invalid input

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Set Timer Duration"),
            content=time_input,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Save", on_click=save_time)
            ]
        )
        self.page.dialog.open = True
        self.page.update()

    def toggle_timer(self, e):
        self.timer_running = not self.timer_running
        if self.timer_running:
            self.play_icon.icon = ft.icons.PAUSE_ROUNDED
            threading.Thread(target=self.run_timer, daemon=True).start()
        else:
            self.play_icon.icon = ft.icons.PLAY_ARROW_ROUNDED
        self.update()

    def run_timer(self):
        while self.timer_running and self.current_seconds > 0:
            mins, secs = divmod(self.current_seconds, 60)
            self.timer_text.value = "{:02d}:{:02d}".format(mins, secs)
            self.current_seconds -= 1
            try:
                self.update()
            except:
                break
            time.sleep(1)

    # --- AUDIO SETTINGS ---
    def open_audio_settings(self, e):
        # (Same logic as before, just kept cleaner)
        def toggle(e, ctrl): ctrl.play() if e.control.value else ctrl.pause()
        def slide(e, ctrl): ctrl.volume = e.control.value / 100; ctrl.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text("Ambient Sounds"),
            content=ft.Column(
                height=200,
                controls=[
                    self._sound_row("Rain", self.audio_rain, toggle, slide),
                    self._sound_row("Wind", self.audio_wind, toggle, slide),
                    self._sound_row("Thunder", self.audio_thunder, toggle, slide),
                ]
            )
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _sound_row(self, name, audio, on_toggle, on_slide):
        return ft.Row(
            controls=[
                ft.Text(name, width=60),
                ft.Switch(on_change=lambda e: on_toggle(e, audio)),
                ft.Slider(min=0, max=100, value=50, expand=True, on_change=lambda e: on_slide(e, audio))
            ]
        )

    def exit_focus(self, e):
        self.audio_rain.pause()
        self.audio_wind.pause()
        self.audio_thunder.pause()
        self.on_exit()

    def build(self):
        return ft.Stack(
            controls=[
                # LAYER 1: Background Image (Cherry Blossom / Scenic)
                ft.Image(
                    src="https://images.unsplash.com/photo-1490750967868-58cb9bdda31c?q=80&w=2070&auto=format&fit=crop",
                    fit=ft.ImageFit.COVER,
                    opacity=0.8,
                    expand=True
                ),
                
                # LAYER 2: Dark Overlay for text readability
                ft.Container(bgcolor=ft.colors.with_opacity(0.4, "black"), expand=True),

                # LAYER 3: Main Content
                ft.Column(
                    expand=True,
                    controls=[
                        # TOP BAR
                        ft.Container(
                            padding=20,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.IconButton(ft.icons.CLOSE, icon_color="white", on_click=self.exit_focus, tooltip="Exit"),
                                    ft.IconButton(ft.icons.TUNE, icon_color="white", on_click=self.open_audio_settings, tooltip="Sounds")
                                ]
                            )
                        ),

                        # CENTER: Timer & Modes
                        ft.Container(
                            expand=True,
                            alignment=ft.alignment.center,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                                controls=[
                                    self.mode_row,          # The pills (Pomodoro etc)
                                    self.timer_container,   # The giant text
                                    self.play_icon,         # Play button
                                    ft.Text(self.task_title, size=16, color="white70") # Current Task
                                ]
                            )
                        ),

                        # BOTTOM BAR
                        ft.Container(
                            padding=30,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    # Spotify Widget (Bottom Left)
                                    GlassCard(
                                        width=220, height=70,
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(ft.icons.MUSIC_NOTE, color="#1DB954"),
                                                ft.Column(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    spacing=0,
                                                    controls=[
                                                        ft.Text("Lofi Beats", size=12, weight="bold"),
                                                        ft.Text("Spotify Web", size=10, color="white54")
                                                    ]
                                                ),
                                                ft.IconButton(ft.icons.SKIP_NEXT, icon_size=20, icon_color="white")
                                            ]
                                        )
                                    ),
                                    
                                    # Complete Button (Bottom Right)
                                    ft.ElevatedButton(
                                        "Finish", 
                                        icon=ft.icons.CHECK, 
                                        bgcolor="white", 
                                        color="black", 
                                        on_click=self.on_complete
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )