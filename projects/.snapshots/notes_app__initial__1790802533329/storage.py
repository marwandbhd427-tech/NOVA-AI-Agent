import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Path to the JSON file that stores notes
STORAGE_PATH = Path(__file__).parent / "notes.json"


@dataclass
class Note:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


def _load_notes() -> List[Note]:
    """Load all notes from the JSON storage file."""
    if not STORAGE_PATH.exists():
        return []
    with STORAGE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [Note(**note) for note in data]


def _save_notes(notes: List[Note]) -> None:
    """Persist the list of notes to the JSON storage file."""
    with STORAGE_PATH.open("w", encoding="utf-8") as f:
        json.dump([asdict(note) for note in notes], f, indent=2)


def list_notes() -> List[Note]:
    """Return a list of all notes."""
    return _load_notes()


def get_note_by_id(note_id: str) -> Optional[Note]:
    """Retrieve a note by its unique identifier."""
    for note in _load_notes():
        if note.id == note_id:
            return note
    return None


def add_note(title: str, content: str) -> Note:
    """Create a new note and persist it."""
    notes = _load_notes()
    note = Note(title=title, content=content)
    notes.append(note)
    _save_notes(notes)
    return note


def update_note(
    note_id: str, title: Optional[str] = None, content: Optional[str] = None
) -> Optional[Note]:
    """Update an existing note's title and/or content."""
    notes = _load_notes()
    for i, note in enumerate(notes):
        if note.id == note_id:
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            note.updated_at = datetime.utcnow().isoformat()
            notes[i] = note
            _save_notes(notes)
            return note
    return None


def delete_note(note_id: str) -> bool:
    """Remove a note by its unique identifier."""
    notes = _load_notes()
    new_notes = [note for note in notes if note.id != note_id]
    if len(new_notes) == len(notes):
        return False  # No note found to delete
    _save_notes(new_notes)
    return True


__all__ = [
    "Note",
    "list_notes",
    "get_note_by_id",
    "add_note",
    "update_note",
    "delete_note",
]