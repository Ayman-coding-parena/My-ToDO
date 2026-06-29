#!/usr/bin/env python3
"""My To-Do — CLI task manager with JSON persistence."""

import argparse
import sys

from progress import render_pie_chart, render_progress_summary
from todo_manager import TodoManager


def format_task(task: dict) -> str:
    status = "[x]" if task["completed"] else "[ ]"
    desc = task.get("description") or ""
    line = f"  {status} #{task['id']}: {task['title']}"
    if desc:
        line += f"\n       {desc}"
    return line


def print_tasks(tasks: list[dict], heading: str = "Tasks") -> None:
    print(f"\n{heading} ({len(tasks)})")
    print("-" * 40)
    if not tasks:
        print("  (none)")
    else:
        for task in tasks:
            print(format_task(task))
    print()


def handle_error(exc: Exception) -> None:
    print(f"Error: {exc}", file=sys.stderr)


def run_interactive(manager: TodoManager) -> None:
    menu = """
╔══════════════════════════════════════╗
║            My To-Do                  ║
╠══════════════════════════════════════╣
║  1. Add task                         ║
║  2. Delete task                      ║
║  3. Mark complete                    ║
║  4. Mark incomplete                  ║
║  5. Edit task                        ║
║  6. List tasks                       ║
║  7. Search tasks                     ║
║  8. Clear completed tasks            ║
║  9. View progress (pie chart)        ║
║  0. Exit                             ║
╚══════════════════════════════════════╝
"""
    while True:
        completed, total, _ = manager.progress_stats()
        print(render_progress_summary(completed, total))
        print(menu)
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Title: ").strip()
                description = input("Description (optional): ").strip()
                task = manager.add_task(title, description)
                print(f"\nAdded task #{task['id']}: {task['title']}\n")

            elif choice == "2":
                task_id = int(input("Task ID to delete: ").strip())
                removed = manager.delete_task(task_id)
                print(f"\nDeleted task #{removed['id']}: {removed['title']}\n")

            elif choice == "3":
                task_id = int(input("Task ID to mark complete: ").strip())
                task = manager.mark_complete(task_id, True)
                print(f"\nMarked complete: #{task['id']} {task['title']}\n")

            elif choice == "4":
                task_id = int(input("Task ID to mark incomplete: ").strip())
                task = manager.mark_complete(task_id, False)
                print(f"\nMarked incomplete: #{task['id']} {task['title']}\n")

            elif choice == "5":
                task_id = int(input("Task ID to edit: ").strip())
                existing = manager.get_task(task_id)
                if existing is None:
                    raise ValueError(f"Task #{task_id} not found.")
                print(f"Current title: {existing['title']}")
                new_title = input("New title (Enter to keep): ").strip()
                print(f"Current description: {existing.get('description', '')}")
                new_desc = input("New description (Enter to keep): ").strip()
                task = manager.edit_task(
                    task_id,
                    title=new_title if new_title else None,
                    description=new_desc if new_desc else None,
                )
                print(f"\nUpdated task #{task['id']}\n")

            elif choice == "6":
                print("Filter: 1=All  2=Active  3=Completed")
                filt = input("Choose filter [1]: ").strip() or "1"
                mapping = {"1": "all", "2": "active", "3": "completed"}
                filter_by = mapping.get(filt, "all")
                tasks = manager.list_tasks(filter_by)
                print_tasks(tasks, f"Tasks ({filter_by})")

            elif choice == "7":
                keyword = input("Search keyword: ").strip()
                results = manager.search_tasks(keyword)
                print_tasks(results, f"Search results for '{keyword}'")

            elif choice == "8":
                count = manager.clear_completed()
                print(f"\nRemoved {count} completed task(s).\n")

            elif choice == "9":
                c, t, _ = manager.progress_stats()
                print(render_pie_chart(c, t))

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option. Please try again.\n")

        except ValueError as exc:
            handle_error(exc)
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="My To-Do — manage tasks from the command line.",
    )
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a new task")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument("-d", "--desc", default="", help="Optional description")

    del_p = sub.add_parser("delete", help="Delete a task by ID")
    del_p.add_argument("id", type=int, help="Task ID")

    done_p = sub.add_parser("complete", help="Mark a task complete")
    done_p.add_argument("id", type=int, help="Task ID")

    undo_p = sub.add_parser("uncomplete", help="Mark a task incomplete")
    undo_p.add_argument("id", type=int, help="Task ID")

    edit_p = sub.add_parser("edit", help="Edit a task")
    edit_p.add_argument("id", type=int, help="Task ID")
    edit_p.add_argument("-t", "--title", help="New title")
    edit_p.add_argument("-d", "--desc", help="New description")

    list_p = sub.add_parser("list", help="List tasks")
    list_p.add_argument(
        "-f",
        "--filter",
        choices=["all", "active", "completed"],
        default="all",
        help="Filter tasks (default: all)",
    )

    search_p = sub.add_parser("search", help="Search tasks by keyword")
    search_p.add_argument("keyword", help="Keyword to search for")

    sub.add_parser("clear-completed", help="Remove all completed tasks")

    sub.add_parser("progress", help="Show progress pie chart")

    return parser


def run_cli(manager: TodoManager, args: argparse.Namespace) -> int:
    try:
        if args.command == "add":
            task = manager.add_task(args.title, args.desc)
            print(f"Added task #{task['id']}: {task['title']}")

        elif args.command == "delete":
            removed = manager.delete_task(args.id)
            print(f"Deleted task #{removed['id']}: {removed['title']}")

        elif args.command == "complete":
            task = manager.mark_complete(args.id, True)
            print(f"Marked complete: #{task['id']} {task['title']}")

        elif args.command == "uncomplete":
            task = manager.mark_complete(args.id, False)
            print(f"Marked incomplete: #{task['id']} {task['title']}")

        elif args.command == "edit":
            if args.title is None and args.desc is None:
                print("Error: provide --title and/or --desc to edit.", file=sys.stderr)
                return 1
            task = manager.edit_task(args.id, title=args.title, description=args.desc)
            print(f"Updated task #{task['id']}: {task['title']}")

        elif args.command == "list":
            tasks = manager.list_tasks(args.filter)
            print_tasks(tasks, f"Tasks ({args.filter})")

        elif args.command == "search":
            results = manager.search_tasks(args.keyword)
            print_tasks(results, f"Search: '{args.keyword}'")

        elif args.command == "clear-completed":
            count = manager.clear_completed()
            print(f"Removed {count} completed task(s).")

        elif args.command == "progress":
            c, t, _ = manager.progress_stats()
            print(render_pie_chart(c, t))

        return 0

    except ValueError as exc:
        handle_error(exc)
        return 1


def main() -> int:
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            reconfigure = getattr(stream, "reconfigure", None)
            if reconfigure is not None:
                try:
                    reconfigure(encoding="utf-8")
                except (OSError, ValueError):
                    pass

    manager = TodoManager()
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        run_interactive(manager)
        return 0

    return run_cli(manager, args)


if __name__ == "__main__":
    sys.exit(main())
