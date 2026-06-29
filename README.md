# My To-Do

A command-line to-do app written in Python. Manage tasks from an interactive menu or with direct CLI commands. All tasks are saved automatically to a JSON file.

## Requirements

- **Python 3.10+**
- No external packages (standard library only)

## Getting Started

Open a terminal in this folder and run:

```powershell
python todo.py
```

On Windows, use `python` — not `/usr/bin/env python3`. The shebang at the top of `todo.py` is for Linux/macOS only.

To check your Python version:

```powershell
python --version
```

## Features

| Feature | Description |
|---|---|
| Add task | Title + optional description |
| Delete task | Remove by task ID |
| Mark complete / incomplete | Toggle completion status |
| Edit task | Change title or description |
| List tasks | Filter by all, active, or completed |
| Search | Find tasks by keyword |
| Clear completed | Remove all finished tasks at once |
| Progress chart | Live ASCII pie chart and progress bar |

## Interactive Menu

Running `python todo.py` with no arguments opens the menu:

```
1. Add task
2. Delete task
3. Mark complete
4. Mark incomplete
5. Edit task
6. List tasks
7. Search tasks
8. Clear completed tasks
9. View progress (pie chart)
0. Exit
```

A progress bar is shown at the top of the menu and updates after every action.

## Command-Line Usage

```powershell
# Add tasks
python todo.py add "Buy groceries" -d "Milk and eggs"
python todo.py add "Walk the dog"

# List tasks
python todo.py list
python todo.py list -f active
python todo.py list -f completed

# Update tasks
python todo.py complete 1
python todo.py uncomplete 1
python todo.py edit 1 -t "New title" -d "Updated description"

# Other commands
python todo.py delete 1
python todo.py search "groceries"
python todo.py clear-completed
python todo.py progress
```

Run `python todo.py --help` for full command reference.

## Data Storage

Tasks are saved to `tasks.json` in this folder. The file is created automatically on the first save.

Example structure:

```json
{
  "next_id": 3,
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk and eggs",
      "completed": false,
      "created_at": "2026-06-29T07:50:04Z"
    }
  ]
}
```

To reset the app, delete `tasks.json`.

## Project Structure

```
ToDO App/
├── todo.py           # Main entry point (menu + CLI)
├── todo_manager.py   # Task logic and JSON persistence
├── progress.py       # Progress bar and pie chart
├── tasks.json        # Saved tasks (auto-generated)
├── requirements.txt
└── README.md
```

## Python Concepts Used

This project demonstrates:

- **Lists** — storing and filtering the task collection
- **Dictionaries** — each task is a dict with id, title, description, etc.
- **File handling** — reading and writing JSON with `json` and `pathlib`

## Troubleshooting

**`/usr/bin/env` is not recognized (Windows)**  
Run with `python todo.py` instead of copying the Unix shebang line.

**Tasks not saving**  
Make sure the app folder is writable. Check that `tasks.json` appears after adding a task.

**Garbled characters in the menu**  
The app sets UTF-8 output on Windows when possible. If box characters still look wrong, use the CLI commands instead of the interactive menu.
