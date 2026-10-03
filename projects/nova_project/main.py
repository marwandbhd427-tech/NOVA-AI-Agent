import os
import sqlite3

# Optional Kivy imports – they are only needed when the GUI is launched.
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.popup import Popup
    from kivy.uix.gridlayout import GridLayout
    from kivy.properties import ObjectProperty
except Exception:
    # Kivy is not available (e.g., during unit testing). Define minimal stubs so
    # that the rest of the module can be imported without errors.
    App = None
    BoxLayout = object
    ScrollView = object
    Label = object
    Button = object
    TextInput = object
    Popup = object
    GridLayout = object
    ObjectProperty = object

DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")


def init_db():
    """Create the notes table if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def load_notes():
    """Return all notes ordered by newest first."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM notes ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def add_note(title, content):
    """Insert a new note into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()


def update_note(note_id, title, content):
    """Update an existing note."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, note_id)
    )
    conn.commit()
    conn.close()


def delete_note(note_id):
    """Delete a note by id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


# GUI classes are defined only when Kivy is available.
if App is not None:

    class NoteItem(BoxLayout):
        """Widget representing a single note in the list."""
        title = ObjectProperty(None)
        edit_btn = ObjectProperty(None)
        delete_btn = ObjectProperty(None)

        def __init__(self, note_id, title_text, content_text, **kwargs):
            super().__init__(orientation="horizontal", size_hint_y=None, height=40, **kwargs)
            self.note_id = note_id
            self.title_text = title_text
            self.content_text = content_text

            self.add_widget(Label(text=title_text, size_hint_x=0.6))
            self.edit_btn = Button(text="Edit", size_hint_x=0.2)
            self.edit_btn.bind(on_release=self.edit_note)
            self.add_widget(self.edit_btn)
            self.delete_btn = Button(text="Delete", size_hint_x=0.2)
            self.delete_btn.bind(on_release=self.delete_note)
            self.add_widget(self.delete_btn)

        def edit_note(self, *args):
            popup = NotePopup(
                self.note_id, self.title_text, self.content_text, self.parent.parent
            )
            popup.open()

        def delete_note(self, *args):
            delete_note(self.note_id)
            parent = self.parent
            if parent:
                parent.remove_widget(self)

    class NotePopup(Popup):
        """Popup for adding or editing a note."""

        def __init__(self, note_id, title_text, content_text, notes_layout, **kwargs):
            super().__init__(
                title="Add Note" if note_id is None else "Edit Note",
                size_hint=(0.8, 0.6),
                **kwargs,
            )
            self.note_id = note_id
            self.notes_layout = notes_layout

            content = GridLayout(cols=1, spacing=10, padding=10)
            self.title_input = TextInput(
                text=title_text, multiline=False, size_hint_y=None, height=40
            )
            self.content_input = TextInput(
                text=content_text, multiline=True, size_hint_y=1
            )
            content.add_widget(Label(text="Title:", size_hint_y=None, height=20))
            content.add_widget(self.title_input)
            content.add_widget(Label(text="Content:", size_hint_y=None, height=20))
            content.add_widget(self.content_input)

            btn_layout = BoxLayout(size_hint_y=None, height=40)
            save_btn = Button(text="Save")
            save_btn.bind(on_release=self.save_note)
            cancel_btn = Button(text="Cancel")
            cancel_btn.bind(on_release=lambda *x: self.dismiss())
            btn_layout.add_widget(save_btn)
            btn_layout.add_widget(cancel_btn)

            content.add_widget(btn_layout)
            self.content = content

        def save_note(self, *args):
            title = self.title_input.text.strip()
            content = self.content_input.text.strip()
            if not title:
                return  # Title is required; silently ignore for brevity.
            if self.note_id is None:
                add_note(title, content)
            else:
                update_note(self.note_id, title, content)
            # Refresh the notes list in the main layout.
            self.notes_layout.clear_widgets()
            for nid, nt, nc in load_notes():
                self.notes_layout.add_widget(
                    NoteItem(nid, nt, nc, size_hint_y=None, height=40)
                )
            self.dismiss()

    class NotesApp(App):
        def build(self):
            root = BoxLayout(orientation="vertical")
            scroll = ScrollView()
            self.notes_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            self.notes_layout.bind(minimum_height=self.notes_layout.setter("height"))
            scroll.add_widget(self.notes_layout)
            root.add_widget(scroll)

            add_btn = Button(text="Add Note", size_hint_y=None, height=50)
            add_btn.bind(on_release=self.open_add_popup)
            root.add_widget(add_btn)

            self.refresh_notes()
            return root

        def refresh_notes(self):
            self.notes_layout.clear_widgets()
            for nid, nt, nc in load_notes():
                self.notes_layout.add_widget(
                    NoteItem(nid, nt, nc, size_hint_y=None, height=40)
                )

        def open_add_popup(self, *args):
            popup = NotePopup(None, "", "", self.notes_layout)
            popup.open()


if __name__ == "__main__":
    init_db()
    if App is not None:
        NotesApp().run()
    else:
        print("Kivy is not installed; GUI cannot be launched.")