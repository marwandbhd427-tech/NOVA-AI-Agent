import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".notes_app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def add_note(content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (content, created_at) VALUES (?, ?)",
        (content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    print("Note added.")

def list_notes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No notes found.")
        return
    for row in rows:
        print(f"[{row['id']}] {row['created_at']} - {row['content']}")

def delete_note(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cursor.rowcount == 0:
        print(f"No note with id {note_id}.")
    else:
        print(f"Note {note_id} deleted.")
    conn.commit()
    conn.close()

def print_help():
    print(
        """
        Notes App Commands:
        add <content>      Add a new note.
        list               List all notes.
        delete <id>        Delete note by its id.
        help               Show this help message.
        exit               Exit the application.
        """
    )

def main():
    init_db()
    print("Welcome to the Notes App! Type 'help' for commands.")
    while True:
        try:
            user_input = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not user_input:
            continue
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "add":
            if not arg:
                print("Error: No content provided.")
            else:
                add_note(arg)
        elif command == "list":
            list_notes()
        elif command == "delete":
            if not arg.isdigit():
                print("Error: Provide a numeric note id.")
            else:
                delete_note(int(arg))
        elif command == "help":
            print_help()
        elif command == "exit":
            print("Goodbye!")
            break
        else:
            print(f"Unknown command: {command}. Type 'help' for options.")

if __name__ == "__main__":
    main()