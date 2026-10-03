#!/usr/bin/env python3
"""
Simple Note-taking application.

This module provides:
- NoteManager: a class to create, read, update, delete, and list notes.
- Persistence to a JSON file (default: notes.json).
- A command‑line interface via argparse.

The module is intentionally pure logic; it does not open any GUI or perform network I/O,
making it suitable for unit testing without side effects.
"""

import json
import os
import argparse
from typing import Dict, List, Optional

DEFAULT_DB = "notes.json"


class Note:
    """Represents a single note."""

    def __init__(self, note_id: int, title: str, content: str):
        self.id = note_id
        self.title = title
        self.content = content

    def to_dict(self) -> Dict:
        return {"id": self.id, "title": self.title, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict) -> "Note":
        return cls(data["id"], data["title"], data["content"])


class NoteManager:
    """Manages a collection of notes with persistence."""

    def __init__(self, db_path: str = DEFAULT_DB):
        self.db_path = db_path
        self.notes: Dict[int, Note] = {}
        self._load()

    def _load(self) -> None:
        """Load notes from the JSON database."""
        if not os.path.exists(self.db_path):
            self.notes = {}
            return
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.notes = {int(k): Note.from_dict(v) for k, v in data.items()}
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, start fresh
            self.notes = {}

    def _save(self) -> None:
        """Persist notes to the JSON database."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v.to_dict() for k, v in self.notes.items()}, f, indent=2)

    def _next_id(self) -> int:
        """Generate the next note ID."""
        return max(self.notes.keys(), default=0) + 1

    def add_note(self, title: str, content: str) -> Note:
        """Create a new note."""
        note_id = self._next_id()
        note = Note(note_id, title, content)
        self.notes[note_id] = note
        self._save()
        return note

    def get_note(self, note_id: int) -> Optional[Note]:
        """Retrieve a note by ID."""
        return self.notes.get(note_id)

    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """Update an existing note. Returns True if successful."""
        note = self.notes.get(note_id)
        if not note:
            return False
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        self._save()
        return True

    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID. Returns True if deleted."""
        if note_id in self.notes:
            del self.notes[note_id]
            self._save()
            return True
        return False

    def list_notes(self) -> List[Note]:
        """Return a list of all notes sorted by ID."""
        return [self.notes[k] for k in sorted(self.notes)]

    def clear_all(self) -> None:
        """Delete all notes (used for testing)."""
        self.notes = {}
        self._save()


def _print_note(note: Note) -> None:
    """Helper to display a note."""
    print(f"ID: {note.id}")
    print(f"Title: {note.title}")
    print("Content:")
    print(note.content)
    print("-" * 40)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple Note-taking CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add
    add_parser = subparsers.add_parser("add", help="Create a new note")
    add_parser.add_argument("title", help="Title of the note")
    add_parser.add_argument("content", help="Content of the note")

    # Get
    get_parser = subparsers.add_parser("get", help="Retrieve a note by ID")
    get_parser.add_argument("id", type=int, help="Note ID")

    # Update
    update_parser = subparsers.add_parser("update", help="Update an existing note")
    update_parser.add_argument("id", type=int, help="Note ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--content", help="New content")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a note by ID")
    delete_parser.add_argument("id", type=int, help="Note ID")

    # List
    subparsers.add_parser("list", help="List all notes")

    args = parser.parse_args()
    manager = NoteManager()

    if args.command == "add":
        note = manager.add_note(args.title, args.content)
        print("Note added:")
        _print_note(note)

    elif args.command == "get":
        note = manager.get_note(args.id)
        if note:
            _print_note(note)
        else:
            print(f"No note found with ID {args.id}")

    elif args.command == "update":
        success = manager.update_note(args.id, title=args.title, content=args.content)
        if success:
            print("Note updated:")
            _print_note(manager.get_note(args.id))
        else:
            print(f"No note found with ID {args.id}")

    elif args.command == "delete":
        success = manager.delete_note(args.id)
        if success:
            print(f"Note {args.id} deleted.")
        else:
            print(f"No note found with ID {args.id}")

    elif args.command == "list":
        notes = manager.list_notes()
        if notes:
            for note in notes:
                _print_note(note)
        else:
            print("No notes available.")


if __name__ == "__main__":
    main()