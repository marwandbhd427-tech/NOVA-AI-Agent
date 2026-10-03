import argparse
import sys
from datetime import datetime
from pathlib import Path

# Import custom modules (assumes notes.py and storage.py are in the same directory)
try:
    from notes import Note
    from storage import load_notes, save_notes
except ImportError as exc:
    print("Required modules not found. Ensure notes.py and storage.py are present.", file=sys.stderr)
    raise exc

NOTES_FILE = Path.home() / ".notes_app" / "notes.json"


def add_note(title: str, content: str) -> None:
    notes = load_notes(NOTES_FILE)
    note_id = max((n.id for n in notes), default=0) + 1
    new_note = Note(
        id=note_id,
        title=title,
        content=content,
        created_at=datetime.utcnow().isoformat()
    )
    notes.append(new_note)
    save_notes(NOTES_FILE, notes)
    print(f"Note added with ID {note_id}.")


def list_notes() -> None:
    notes = load_notes(NOTES_FILE)
    if not notes:
        print("No notes found.")
        return
    print(f"{'ID':<5} {'Title':<30} {'Created At'}")
    print("-" * 60)
    for note in notes:
        print(f"{note.id:<5} {note.title:<30} {note.created_at}")


def view_note(note_id: int) -> None:
    notes = load_notes(NOTES_FILE)
    for note in notes:
        if note.id == note_id:
            print(f"ID: {note.id}")
            print(f"Title: {note.title}")
            print(f"Created At: {note.created_at}")
            print("-" * 40)
            print(note.content)
            return
    print(f"Note with ID {note_id} not found.")


def delete_note(note_id: int) -> None:
    notes = load_notes(NOTES_FILE)
    new_notes = [n for n in notes if n.id != note_id]
    if len(new_notes) == len(notes):
        print(f"Note with ID {note_id} not found.")
        return
    save_notes(NOTES_FILE, new_notes)
    print(f"Note with ID {note_id} deleted.")


def parse_args():
    parser = argparse.ArgumentParser(description="Simple CLI Notes Application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("-t", "--title", required=True, help="Title of the note")
    add_parser.add_argument("-c", "--content", required=True, help="Content of the note")

    # List command
    subparsers.add_parser("list", help="List all notes")

    # View command
    view_parser = subparsers.add_parser("view", help="View a note by ID")
    view_parser.add_argument("id", type=int, help="ID of the note to view")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a note by ID")
    delete_parser.add_argument("id", type=int, help="ID of the note to delete")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.command == "add":
        add_note(args.title, args.content)
    elif args.command == "list":
        list_notes()
    elif args.command == "view":
        view_note(args.id)
    elif args.command == "delete":
        delete_note(args.id)
    else:
        print("Unknown command")


if __name__ == "__main__":
    # Ensure the storage directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    main()