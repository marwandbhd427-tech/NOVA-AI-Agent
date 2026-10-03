import argparse
import datetime
import os
import sqlite3
import sys
from contextlib import closing

DB_FILE = os.path.join(os.path.expanduser("~"), ".notes_app.db")


def init_db() -> None:
    """Create the notes database and table if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_note(title: str, content: str) -> int:
    """Insert a new note into the database and return its ID."""
    now = datetime.datetime.utcnow().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute(
            """
            INSERT INTO notes (title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, content, now, now),
        )
        conn.commit()
        return cur.lastrowid


def list_notes() -> list[tuple[int, str, str]]:
    """Return a list of all notes (id, title, created_at)."""
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute(
            """
            SELECT id, title, created_at FROM notes ORDER BY created_at DESC
            """
        )
        return cur.fetchall()


def get_note(note_id: int) -> tuple[int, str, str, str, str] | None:
    """Return a single note by ID, or None if not found."""
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute(
            """
            SELECT id, title, content, created_at, updated_at
            FROM notes WHERE id = ?
            """,
            (note_id,),
        )
        return cur.fetchone()


def delete_note(note_id: int) -> bool:
    """Delete a note by ID. Returns True if a row was deleted."""
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cur.rowcount > 0


def update_note(note_id: int, title: str | None, content: str | None) -> bool:
    """Update title and/or content of a note. Returns True if updated."""
    if title is None and content is None:
        return False
    fields = []
    values = []
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if content is not None:
        fields.append("content = ?")
        values.append(content)
    values.append(datetime.datetime.utcnow().isoformat())
    values.append(note_id)
    query = f"UPDATE notes SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute(query, tuple(values))
        conn.commit()
        return cur.rowcount > 0


def print_note(note: tuple[int, str, str, str, str]) -> None:
    """Print a note in a readable format."""
    note_id, title, content, created, updated = note
    print(f"ID: {note_id}")
    print(f"Title: {title}")
    print(f"Created: {created}")
    print(f"Updated: {updated}")
    print("-" * 40)
    print(content)
    print("-" * 40)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple CLI notes application. Stores notes in a local SQLite database."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add
    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("title", help="Title of the note")
    add_parser.add_argument("content", help="Content of the note")

    # List
    subparsers.add_parser("list", help="List all notes")

    # View
    view_parser = subparsers.add_parser("view", help="View a note by ID")
    view_parser.add_argument("id", type=int, help="ID of the note to view")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a note by ID")
    delete_parser.add_argument("id", type=int, help="ID of the note to delete")

    # Update
    update_parser = subparsers.add_parser("update", help="Update a note")
    update_parser.add_argument("id", type=int, help="ID of the note to update")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--content", help="New content")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    init_db()
    args = parse_args(argv)

    if args.command == "add":
        note_id = add_note(args.title, args.content)
        print(f"Note added with ID {note_id}")

    elif args.command == "list":
        notes = list_notes()
        if not notes:
            print("No notes found.")
        else:
            print(f"{'ID':<5} {'Title':<30} {'Created':<20}")
            print("-" * 60)
            for note_id, title, created in notes:
                print(f"{note_id:<5} {title[:30]:<30} {created:<20}")

    elif args.command == "view":
        note = get_note(args.id)
        if note:
            print_note(note)
        else:
            print(f"Note with ID {args.id} not found.", file=sys.stderr)

    elif args.command == "delete":
        if delete_note(args.id):
            print(f"Deleted note {args.id}.")
        else:
            print(f"Note with ID {args.id} not found.", file=sys.stderr)

    elif args.command == "update":
        if update_note(args.id, args.title, args.content):
            print(f"Updated note {args.id}.")
        else:
            print(
                f"Nothing to update or note with ID {args.id} not found.",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()