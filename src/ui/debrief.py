import flet as ft
from src.ui.components.glass_card import GlassCard
from src.services.local_db import get_local_tasks

class DailyDebrief(ft.UserControl):
    def __init__(self, page, on_back):
        super().__init__()
        self.page = page
        self.on_back = on_back
        
        # Create empty controls that we will update later
        self.tasks_completed_text = ft.Text("0", size=40, weight="bold")
        self.hours_focused_text = ft.Text("0.0", size=40, weight="bold")
        self.wins_list = ft.Column(spacing=10)

    def did_mount(self):
        # This runs EVERY TIME the component is shown
        self.refresh_stats()

    def refresh_stats(self):
        # 1. Fetch fresh data
        all_tasks = get_local_tasks(include_completed=True)
        completed_tasks = [t for t in all_tasks if t.get('completed', False)]
        
        count_completed = len(completed_tasks)
        hours_focused = round(count_completed * 0.4, 1) # Approx 25 mins per task

        # 2. Update the UI controls
        self.tasks_completed_text.value = str(count_completed)
        self.hours_focused_text.value = str(hours_focused)
        
        # 3. Rebuild the list of wins
        self.wins_list.controls.clear()
        for t in completed_tasks:
            self.wins_list.controls.append(self.create_win_row(t))
        
        self.update()

    def build(self):
        return ft.Container(
            expand=True,
            padding=40,
            content=ft.Column(
                controls=[
                    # Header
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text("Daily Debrief", size=32, weight="bold", color="#BB86FC"),
                                    ft.Text("Summary of your wins", color="white54")
                                ]
                            ),
                            ft.OutlinedButton("Back to Dashboard", on_click=self.on_back)
                        ]
                    ),
                    ft.Container(height=20),

                    # Stats Row
                    ft.Row(
                        controls=[
                            self.create_stat_card("Tasks Completed", self.tasks_completed_text, ft.icons.EMOJI_EVENTS),
                            self.create_stat_card("Hours Focused", self.hours_focused_text, ft.icons.ACCESS_TIME_FILLED),
                        ]
                    ),

                    ft.Container(height=30),

                    # List of Wins
                    ft.Text("Today's Accomplishments", size=16, weight="bold"),
                    ft.Container(
                        expand=True,
                        content=ft.ListView(
                            expand=True,
                            spacing=10,
                            controls=[self.wins_list] # We put the column inside the listview
                        )
                    )
                ]
            )
        )

    def create_stat_card(self, label, value_control, icon):
        return GlassCard(
            width=250, height=120, padding=20,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[ft.Text(label, size=12, weight="bold"), ft.Icon(icon, color="white24")]
                    ),
                    value_control # Pass the dynamic text control here
                ]
            )
        )

    def create_win_row(self, task):
        return ft.Container(
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.05, "white"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(controls=[
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="#00C853", size=20),
                        ft.Container(width=10),
                        ft.Text(task['title'], weight="bold")
                    ]),
                ]
            )
        )