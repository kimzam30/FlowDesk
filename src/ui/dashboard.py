import flet as ft
import datetime
import threading
import time
from src.ui.components.glass_card import GlassCard
from src.services.github_sync import fetch_my_issues
from src.services.local_db import get_local_tasks, add_local_task, mark_task_complete

class Dashboard(ft.UserControl):
    def __init__(self, page, on_start_focus, on_show_debrief):
        super().__init__()
        self.page = page
        self.on_start_focus = on_start_focus
        self.on_show_debrief = on_show_debrief
        
        # UI State
        self.clock_text = ft.Text("00:00:00", size=32, weight="bold", color="#E0E0E0", font_family="monospace")
        self.date_text = ft.Text("", size=14, color="white54")
        self.task_column = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
        
        # Input Field
        self.input_task = ft.TextField(
            hint_text="Add a quick task (e.g., Buy milk)...",
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            border_radius=15,
            border_color="transparent",
            color="white",
            expand=True,
            on_submit=self.add_manual_task 
        )

        # Start Clock
        self.running = True
        self.th = threading.Thread(target=self.update_clock, args=(), daemon=True)
        self.th.start()

    def update_clock(self):
        while self.running:
            now = datetime.datetime.now()
            self.clock_text.value = now.strftime("%I:%M:%S %p")
            self.date_text.value = now.strftime("%a, %b %d, %Y")
            try:
                self.update()
            except:
                pass
            time.sleep(1)

    def did_mount(self):
        self.load_tasks()

    def add_manual_task(self, e):
        if not self.input_task.value:
            return
        add_local_task(self.input_task.value)
        self.input_task.value = ""
        self.load_tasks()
        self.update()

    def toggle_task(self, task_id, current_value):
        # Toggle the task state
        mark_task_complete(task_id, is_complete=current_value)
        self.load_tasks()

    def load_tasks(self):
        self.task_column.controls.clear()
        
        # hero section with greeting
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12: greeting = "Good Morning,"
        elif 12 <= hour < 17: greeting = "Good Afternoon,"
        else: greeting = "Good Evening,"

        self.task_column.controls.append(
            ft.Container(
                padding=ft.padding.only(bottom=20),
                content=ft.Column(
                    controls=[
                        ft.Text(f"{greeting} hakim !", size=28, weight="bold"),
                        ft.Text("Lets get to work ", size=16, color="white54", italic=True),
                        ft.Container(height=10),
                        ft.Container(
                            height=1, 
                            bgcolor=ft.colors.with_opacity(0.1, "white") # A subtle divider line
                        )
                    ]
                )
            )
        )
        #end of hero
        
        # 1. Fetch Data
        try:
            gh_issues = fetch_my_issues()
        except:
            gh_issues = []
            
        # CRITICAL: Ensure local_db.py allows 'include_completed'
        local_tasks = get_local_tasks(include_completed=True)

        # 2. Section: Manual Tasks
        if local_tasks:
            self.task_column.controls.append(ft.Text("MY TASKS", size=12, color="#BB86FC", weight="bold"))
            for t in local_tasks:
                is_done = t.get('completed', False)
                card = self.create_task_card(
                    title=t['title'], 
                    subtitle="Manual Entry", 
                    is_manual=True,
                    task_id=t['id'],
                    is_done=is_done
                )
                self.task_column.controls.append(card)

        # 3. Section: GitHub Issues
        if gh_issues:
            self.task_column.controls.append(ft.Container(height=10))
            self.task_column.controls.append(ft.Text("GITHUB ISSUES", size=12, color="#BB86FC", weight="bold"))
            for issue in gh_issues:
                self.task_column.controls.append(self.create_task_card(
                    title=issue['title'], 
                    subtitle=f"Repo: {issue['repo']}",
                    is_manual=False
                ))

        if not local_tasks and not gh_issues:
             self.task_column.controls.append(
                ft.Text("No active tasks. Time to relax?", color="white24", italic=True)
            )

        self.update()

    def create_task_card(self, title, subtitle, is_manual, task_id=None, is_done=False):
        # 1. Define the Style Object correctly
        # This tells Flet: "Make a style that has a line through it"
        task_style = ft.TextStyle(
            decoration=ft.TextDecoration.LINE_THROUGH if is_done else ft.TextDecoration.NONE,
            color=ft.colors.with_opacity(0.5, "white") if is_done else "white",
            weight=ft.FontWeight.BOLD
        )

        return GlassCard(
            width=600,
            height=80,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(controls=[
                        ft.Checkbox(
                            value=is_done, 
                            on_change=lambda e: self.toggle_task(task_id, e.control.value) if is_manual else None
                        ),
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=2,
                            controls=[
                                # 2. Apply the style object to the Text
                                ft.Text(
                                    title, 
                                    size=16, 
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    style=task_style # <--- This is the key fix
                                ),
                                ft.Text(subtitle, size=12, color="white54")
                            ]
                        )
                    ]),
                    # Hide Play button if done
                    ft.Container(
                        visible=not is_done,
                        content=ft.IconButton(
                            ft.icons.PLAY_ARROW, 
                            icon_color="#BB86FC", 
                            tooltip="Focus Mode",
                            on_click=lambda e: self.on_start_focus(task_id, title)
                        )
                    )
                ]
            )
        )

    def build(self):
        return ft.Column(
            expand=True,
            controls=[
                # HEADER
                ft.Container(
                    padding=ft.padding.only(left=30, right=30, top=30, bottom=20),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("FlowDeck", size=32, weight="bold", color="#E0E0E0"),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=0,
                                controls=[self.clock_text, self.date_text]
                            )
                        ]
                    )
                ),
                
                # INPUT AREA
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=30),
                    content=ft.Row(
                        controls=[
                            self.input_task,
                            ft.IconButton(
                                ft.icons.ADD_ROUNDED, 
                                icon_color="#BB86FC", 
                                icon_size=40,
                                on_click=self.add_manual_task
                            )
                        ]
                    )
                ),

                # TASK LIST
                ft.Container(
                    padding=30,
                    expand=True,
                    content=self.task_column
                ),
                
                # FOOTER
                ft.Container(
                    padding=20,
                    alignment=ft.alignment.bottom_right,
                    content=ft.ElevatedButton(
                        "View Debrief",
                        icon=ft.icons.ANALYTICS,
                        bgcolor="#BB86FC",
                        color="black",
                        on_click=lambda e: self.on_show_debrief()
                    )
                )
            ]
        )