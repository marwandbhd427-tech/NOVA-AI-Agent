import json
import os
import uuid

# Optional GUI dependencies – load only if available
try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox, ttk
except Exception:
    tk = None
    simpledialog = None
    messagebox = None
    ttk = None

# ---------- Note Management ----------
class Note:
    def __init__(self, title, content, note_id=None):
        self.id = note_id or str(uuid.uuid4())
        self.title = title
        self.content = content

    def to_dict(self):
        return {"id": self.id, "title": self.title, "content": self.content}

    @staticmethod
    def from_dict(data):
        return Note(data["title"], data["content"], data["id"])


class NoteManager:
    def __init__(self, storage_path="notes.json"):
        self.storage_path = storage_path
        self.notes = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        note = Note.from_dict(item)
                        self.notes[note.id] = note
            except Exception:
                # If file is corrupted, start fresh
                self.notes = {}

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([n.to_dict() for n in self.notes.values()], f, indent=2)

    def add_note(self, title, content):
        note = Note(title, content)
        self.notes[note.id] = note
        self._save()
        return note

    def edit_note(self, note_id, title=None, content=None):
        if note_id not in self.notes:
            raise KeyError("Note not found")
        note = self.notes[note_id]
        if title is not None:
            note.title = title