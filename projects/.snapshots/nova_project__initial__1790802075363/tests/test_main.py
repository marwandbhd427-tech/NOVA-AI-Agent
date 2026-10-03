import json
import os
import sys
import threading
from datetime import datetime

# Path to store notes
DATA_FILE = os.path.join(os.path.expanduser("~"), ".phone_notes.json")

def load_notes():
    """Load notes from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_notes(notes):
    """Save notes to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def add_note(title, content):
    """Add a new note."""
    notes = load_notes()
    note = {
        "id": datetime.utcnow().timestamp(),
        "title": title,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    }
    notes.append(note)
    save_notes(notes)
    return note

def list_notes():
    """Return a list of all notes."""
    return load_notes()

def delete_note(note_id):
    """Delete a note by its ID."""
    notes = load_notes()
    new_notes = [n for n in notes if n["id"] != note_id]
    if len(notes) == len(new_notes):
        return False
    save_notes(new_notes)
    return True

def get_note(note_id):
    """Retrieve a note by its ID."""
    for note in load_notes():
        if note["id"] == note_id:
            return note
    return None

# Simple command-line interface for non-GUI usage
def cli():
    while True:
        print("\n=== Phone Notes CLI ===")
        print("1. List notes")
        print("2. Add note")
        print("3. View note")
        print("4. Delete note")
        print("5. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            notes = list_notes()
            if not notes:
                print("No notes found.")
            else:
                for n in notes:
                    print(f"[{n['id']:.0f}] {n['title']} (Created: {n['created_at']})")
        elif choice == "2":
            title = input("Title: ").strip()
            content = input("Content: ").strip()
            note = add_note(title, content)
            print(f"Note added with ID {note['id']:.0f}.")
        elif choice == "3":
            try:
                note_id = float(input("Enter note ID: ").strip())
            except ValueError:
                print("Invalid ID.")
                continue
            note = get_note(note_id)
            if note:
                print(f"\nTitle: {note['title']}\nCreated: {note['created_at']}\nContent:\n{note['content']}")
            else:
                print("Note not found.")
        elif choice == "4":
            try:
                note_id = float(input("Enter note ID to delete: ").strip())
            except ValueError:
                print("Invalid ID.")
                continue
            if delete_note(note_id):
                print("Note deleted.")
            else:
                print("Note not found.")