import json
import os
import datetime

DB_FILE = "my_tasks.json"

def get_local_tasks(include_completed=False):
    # If file doesn't exist, return empty list
    if not os.path.exists(DB_FILE):
        return []
    
    try:
        with open(DB_FILE, "r") as f:
            tasks = json.load(f)
            # Filter out tasks that are marked 'completed' (optional)
            return [t for t in tasks if not t.get('completed', False)]
    except:
        return []

def add_local_task(title):
    tasks = get_local_tasks()
    new_task = {
        "id": int(datetime.datetime.now().timestamp()), # Unique ID based on time
        "title": title,
        "type": "manual", # To distinguish from GitHub
        "completed": False,
        "created_at": str(datetime.datetime.now())
    }
    tasks.insert(0, new_task) # Add to top
    save_tasks(tasks)
    return tasks

def mark_task_complete(task_id):
    tasks = get_local_tasks()
    for t in tasks:
        if t['id'] == task_id:
            t['completed'] = True
    save_tasks(tasks)

def save_tasks(tasks):
    with open(DB_FILE, "w") as f:
        json.dump(tasks, f, indent=4)