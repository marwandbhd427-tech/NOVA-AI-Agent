import argparse
import json
import os
import sys
import datetime
from pathlib import Path

NOTES_FILE = Path.home() / ".python_note_app" / "notes.json"

def ensure_storage():
    """Ensure the storage directory and file exist."""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text(json.dumps([]))

def load_notes():
    """Load notes from the JSON file."""
    ensure_storage()
    try:
        with NOTES_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_notes(notes):
    """Save notes to the JSON file."""
    with NOTES_FILE.open("w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

def generate_id(notes):
    """Generate a unique integer ID."""
    existing_ids = {note["id"] for note in notes}
    new_id = 1
    while new_id in existing_ids:
        new_id += 1
    return new_id

def add_note(title, content):
    notes = load_notes()
    note = {
        "id": generate_id(notes),
        "title": title,
        "content": content,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }
    notes.append(note)
    save_notes(notes)
    print(f"Note added with ID {note['id']}")

def list_notes():
    notes = load_notes()
    if not notes:
        print("No notes found.")
        return
    for note in notes:
        print(f"[{note['id']}] {note['title']} (Created: {note['created_at']})")

def view_note(note_id):
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id:
            print(f"ID: {note['id']}")
            print(f"Title: {note['title']}")
            print(f"Created: {note['created_at']}")
            print(f"Updated: {note['updated_at']}")
            print("Content:")
            print(note["content"])
            return
    print(f"No note found with ID {note_id}")

def edit_note(note_id, title=None, content=None):
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id:
            if title is not None:
                note["title"] = title
            if content is not None:
                note["content"] = content
            note["updated_at"] = datetime.datetime.now().isoformat()
            save_notes(notes)
            print(f"Note {note_id} updated.")
            return
    print(f"No note found with ID {note_id}")

def delete_note(note_id):
    notes = load_notes()
    new_notes = [note for note in notes if note["id"] != note_id]
    if len(new_notes) == len(notes):
        print(f"No note found with ID {note_id}")
        return
    save_notes(new_notes)
    print(f"Note {note_id} deleted.")

def parse_args():
    parser = argparse.ArgumentParser(description="Simple note-taking CLI application.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add note
    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("title", help="Title of the note")
    add_parser.add_argument("content", help="Content of the note")

    # List notes
    subparsers.add_parser("list", help="List all notes")

    # View note
    view_parser = subparsers.add_parser("view", help="View a note by ID")
    view_parser.add_argument("id", type=int, help="ID of the note to view")

    # Edit note
    edit_parser = subparsers.add_parser("edit", help="Edit a note by ID")
    edit_parser.add_argument("id", type=int, help="ID of the note to edit")
    edit_parser.add_argument("--title", help="New title")
    edit_parser.add_argument("--content", help="New content")

    # Delete note
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
    elif args.command == "edit":
        if args.title is None and args.content is None:
            print("Nothing to update. Use --title and/or --content.")
            return
        edit_note(args.id, title=args.title, content=args.content)
    elif args.command == "delete":
        delete_note(args.id)

if __name__ == "__main__":
    main()