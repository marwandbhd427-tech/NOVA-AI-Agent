import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty

DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")


def init_db():
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM notes ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def add_note(title, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()


def update_note(note_id, title, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, note_id)
    )
    conn.commit()
    conn.close()


def delete_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


class NoteItem(BoxLayout):
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
        popup = NotePopup(self.note_id, self.title_text, self.content_text, self.parent.parent.parent)
        popup.open()

    def delete_note(self, *args):
        delete_note(self.note_id)
        parent = self.parent
        if parent:
            parent.remove_widget(self)


class NotePopup(Popup):
    def __init__(self, note_id, title_text, content_text, notes_layout, **kwargs):
        super().__init__(title="Add Note" if note_id is None else "Edit Note", size_hint=(0.8, 0.6), **kwargs)
        self.note_id = note_id
        self.notes_layout = notes_layout

        content = GridLayout(cols=1, spacing=10, padding=10)
        self.title_input = TextInput(text=title_text, multiline=False, size_hint_y=None, height=40)
        self.content_input = TextInput(text=content_text, multiline=True, size_hint_y=1)
        content.add_widget(Label(text="Title:", size_hint_y=None, height=20))
        content.add_widget(self.title_input)
        content.add_widget(Label(text="Content:", size_hint_y=None, height=20))
        content.add_widget(self.content_input)

        btn_layout = BoxLayout(size_hint_y=None, height=40)
        save_btn = Button(text="Save")
        save_btn.bind(on_release=self.save_note)