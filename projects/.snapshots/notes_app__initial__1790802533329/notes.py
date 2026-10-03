#!/usr/bin/env python3
"""
notes_app - Lightweight notes application for mobile devices.
This script provides a command-line interface to create, list, view, and delete notes.
Notes are stored in a JSON file in the user's home directory.

Usage:
    python main.py add "Title" "Content"   # Add a new note
    python main.py list                    # List all notes
    python main.py view <id>               # View a specific note
    python main.py delete <id>             # Delete a note
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
# Storage layer
# --------------------------------------------------------------------------- #

class Storage:
    """Handles persistence of notes in a JSON file."""
    def __init__(self, file_path: Path | str | None = None):
        if file_path is None:
            # Default to ~/.notes_app/notes.json
            self.file_path = Path.home() / ".notes_app" / "notes.json"
        else:
            self.file_path = Path(file_path).expanduser()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, notes: list[dict]) -> None:
        self.file_path.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_all(self) -> list[dict]:
        return self._load()

    def get(self, note_id: str) -> dict | None:
        for note in self._load():
            if note["id"] == note_id:
                return note
        return None

    def add(self, title: str, content: str) -> dict:
        notes = self._load()
        note = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        notes.append(note)
        self._save(notes)
        return note

    def delete(self, note_id: str) -> bool:
        notes = self._load()
        new_notes = [n for n in notes if n["id"] != note_id]
        if len(new_notes) == len(notes):
            return False
        self._save(new_notes)
        return True

    def update(self, note_id: str, title: str | None, content: str | None) -> dict | None:
        notes = self._load()
        for note in notes:
            if note["id"] == note_id:
                if title is not None:
                    note["title"] = title
                if content is not None:
                    note["content"] = content
                note["updated_at"] = datetime.utcnow().isoformat() + "Z"
                self._save(notes)
                return note
        return None

# --------------------------------------------------------------------------- #
# Application logic
# --------------------------------------------------------------------------- #

class NotesApp:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add(self, title: str, content: str) -> None:
        note = self.storage.add(title, content)
        print(f"Note added with ID: {note['id']}")

    def list(self) -> None:
        notes = self.storage.get_all()
        if not notes:
            print("No notes found.")
            return
        for note in notes:
            print(f"{note['id']}\t{note['title']}\t{note['created_at']}")

    def view(self, note_id: str) -> None:
        note = self.storage.get(note_id)
        if not note:
            print(f"Note with ID {note_id} not found.")
            return
        print(f"ID: {note['id']}")
        print(f"Title: {note['title']}")
        print(f"Created at: {note['created_at']}")
        print(f"Updated at: {note['updated_at']}")
        print("Content:")
        print(note['content'])

    def delete(self, note_id: str) -> None:
        success = self.storage.delete(note_id)
        if success:
            print(f"Note {note_id} deleted.")
        else:
            print(f"Note {note_id} not found.")

    def update(self, note_id: str, title: str | None, content: str | None) -> None:
        note = self.storage.update(note_id, title, content)
        if note:
            print(f"Note {note_id} updated.")
        else:
            print(f"Note {note_id} not found.")

# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description="Simple notes application.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    parser_add = subparsers.add_parser("add", help="Add a new note")
    parser_add.add_argument("title", help="Title of the note")
    parser_add.add_argument("content", help="Content of the note")

    # list
    subparsers.add_parser("list", help="List all notes")

    # view
    parser_view = subparsers.add_parser("view", help="View a note by ID")
    parser_view.add_argument("id", help="ID of the note")

    # delete
    parser_delete = subparsers.add_parser("delete", help="Delete a note by ID")
    parser_delete.add_argument("id", help="ID of the note")

    # update
    parser_update = subparsers.add_parser("update", help="Update a note by ID")
    parser_update.add_argument("id", help="ID of the note")
    parser_update.add_argument("--title", help="New title")
    parser_update.add_argument("--content", help="New content")

    args = parser.parse_args()

    storage = Storage()
    app = NotesApp(storage)

    if args.command == "add":
        app.add(args.title, args.content)
    elif args.command == "list":
        app.list()
    elif args.command == "view":
        app.view(args.id)
    elif args.command == "delete":
        app.delete(args.id)
    elif args.command == "update":
        if not args.title and not args.content:
            print("Nothing to update. Provide --title and/or --content.")
            sys.exit(1)
        app.update(args.id, args.title, args.content)

if __name__ == "__main__":
    main()