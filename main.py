import flet as ft
from src.ui.components.ambient_bg import get_ambient_background
from src.ui.dashboard import Dashboard
from src.ui.focus_mode import FocusMode
from src.ui.debrief import DailyDebrief
from src.services.local_db import mark_task_complete # <--- Import this

def main(page: ft.Page):
    page.title = "FlowDeck"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#050505"

    current_view_container = ft.Container(expand=True)

    def show_dashboard(e=None):
        dashboard = Dashboard(
            page, 
            on_start_focus=start_focus_mode,
            on_show_debrief=show_debrief
        )
        current_view_container.content = dashboard
        page.update()

    # FIX: Accept task_id and title
    def start_focus_mode(task_id, task_title):
        focus_view = FocusMode(
            page, 
            task_title=task_title, 
            on_exit=show_dashboard,
            # FIX: When 'Complete' is clicked, mark DB then show debrief
            on_complete=lambda e: complete_and_debrief(task_id)
        )
        current_view_container.content = focus_view
        page.update()

    def complete_and_debrief(task_id):
        # 1. Update the Database
        mark_task_complete(task_id, is_complete=True)
        # 2. Go to Debrief
        show_debrief()

    def show_debrief(e=None):
        debrief_view = DailyDebrief(
            page,
            on_back=show_dashboard
        )
        current_view_container.content = debrief_view
        page.update()

    layout = ft.Stack(
        expand=True,
        controls=[
            get_ambient_background(page.window_width, page.window_height),
            current_view_container
        ]
    )
    
    page.add(layout)
    show_dashboard()

if __name__ == "__main__":
    ft.app(target=main)