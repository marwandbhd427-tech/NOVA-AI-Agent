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
    def __init__(self, title: str, content: str, note_id: str | None = None):
        self.id = note_id or str(uuid.uuid4())
        self.title = title
        self.content = content

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "content": self.content}

    @staticmethod
    def from_dict(data: dict) -> "Note":
        return Note(data["title"], data["content"], data["id"])

    def __repr__(self) -> str:
        return f"Note(id={self.id!r}, title={self.title!r})"


class NoteManager:
    def __init__(self, storage_path: str = "notes.json"):
        self.storage_path = storage_path
        self.notes: dict[str, Note] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            note = Note.from_dict(item)
                            self.notes[note.id] = note
            except Exception:
                # If file is corrupted or unreadable, start fresh
                self.notes = {}

    def _save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([n.to_dict() for n in self.notes.values()], f, indent=2)

    def add_note(self, title: str, content: str) -> Note:
        note = Note(title, content)
        self.notes[note.id] = note
        self._save()
        return note

    def edit_note(self, note_id: str, title: str | None = None, content: str | None = None) -> Note:
        if note_id not in self.notes:
            raise KeyError("Note not found")
        note = self.notes[note_id]
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        self._save()
        return note

    def delete_note(self, note_id: str) -> None:
        if note_id in self.notes:
            del self.notes[note_id]
            self._save()
        else:
            raise KeyError("Note not found")

    def get_note(self, note_id: str) -> Note | None:
        return self.notes.get(note_id)

    def list_notes(self) -> list[Note]:
        return list(self.notes.values())

    def __iter__(self):
        return iter(self.notes.values())


# ---------- Optional simple CLI for manual use ----------
def _cli():
    manager = NoteManager()
    print("Simple Note Manager CLI")
    while True:
        cmd = input("\nCommands: add, edit, delete, list, exit\n> ").strip().lower()
        if cmd == "add":
            title = input("Title: ")
            content = input("Content: ")
            note = manager.add_note(title, content)
            print(f"Added note {note.id}")
        elif cmd == "edit":
            note_id = input("Note ID: ")
            if note_id not in manager.notes:
                print("Note not found")
                continue
            title = input("New title (leave empty to keep): ")
            content = input("New content (leave empty to keep): ")
            kwargs = {}
            if title:
                kwargs["title"] = title
            if content:
                kwargs["content"] = content
            try:
                manager.edit_note(note_id, **kwargs)
                print("Note updated")
            except KeyError:
                print("Note not found")
        elif cmd == "delete":
            note_id = input("Note ID: ")
            try:
                manager.delete_note(note_id)
                print("Note deleted")
            except KeyError:
                print("Note not found")
        elif cmd == "list":
            for n in manager.list_notes():
                print(f"{n.id}: {n.title}")
        elif cmd == "exit":
            break
        else:
            print("Unknown command")


if __name__ == "__main__":
    # If tkinter is available, launch a very small GUI; otherwise fall back to CLI
    if tk is not None:
        root = tk.Tk()
        root.title("Note Manager")
        label = ttk.Label(root, text="This is a placeholder GUI.\nRun tests with the CLI.")
        label.pack(padx=20, pady=20)
        root.mainloop()
    else:
        _cli()