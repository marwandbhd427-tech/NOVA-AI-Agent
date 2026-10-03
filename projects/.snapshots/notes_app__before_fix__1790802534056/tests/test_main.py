#!/usr/bin/env python3
import argparse
import uuid
from datetime import datetime

import storage

def parse_args():
    parser = argparse.ArgumentParser(description="Notes CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("-t", "--title", required=True, help="Title of the note")
    add_parser.add_argument("-c", "--content", required=True, help="Content of the note")

    subparsers.add_parser("list", help="List all notes")

    view_parser = subparsers.add_parser("view", help="View a note")
    view_parser.add_argument("id", help="ID of the note")

    delete_parser = subparsers.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("id", help="ID of the note")

    return parser.parse_args()

def load_notes():
    return storage.load_notes()

def save_notes(notes):
    storage.save_notes(notes)

def add_note(title, content):
    notes = load_notes()
    note_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    note = {
        "id": note_id,
        "title": title,
        "content": content,
        "created_at": now,
        "updated_at": now,
    }
    notes.append(note)
    save_notes(notes)
    print(f"Note added with ID {note_id}")

def list_notes():
    notes = load_notes()
    if not notes:
        print("No notes found.")
        return
    for n in notes:
        print(f"{n['id']}: {n['title']}")

def view_note(note_id):
    notes = load_notes()
    for n in notes:
        if n["id"] == note_id:
            print(f"ID: {n['id']}")
            print(f"Title: {n['title']}")
            print(f"Created: {n['created_at']}")
            print(f"Updated: {n['updated_at']}")
            print("Content:")
            print(n["content"])
            return
    print(f"No note found with ID {note_id}")

def delete_note(note_id):
    notes = load_notes()
    new_notes = [n for n in notes if n["id"] != note_id]
    if len(new_notes) == len(notes):
        print(f"No note found with ID {note_id}")
        return
    save_notes(new_notes)
    print(f"Note {note_id} deleted.")

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

if __name__ == "__main__":
    main()