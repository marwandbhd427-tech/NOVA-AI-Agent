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
        # Remove from UI
        parent = self.parent
        if parent:
            parent.remove_widget(self)


class NotePopup(Popup):
    def __init__(self, note_id, title_text, content_text, notes_layout, **kwargs):
        super().__init__(title="Edit Note", size_hint=(0.8, 0.6), **kwargs)
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
        cancel_btn = Button(text="Cancel")
        cancel_btn.bind(on_release=self.dismiss)
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)

        main_layout = BoxLayout(orientation="vertical")
        main_layout.add_widget(content)
        main_layout.add_widget(btn_layout)
        self.content = main_layout

    def save_note(self, *args):
        new_title = self.title_input.text.strip()
        new_content = self.content_input.text.strip()
        if new_title and new_content:
            update_note(self.note_id, new_title, new_content)
            # Refresh UI
            self.notes_layout.clear_widgets()
            for nid, title, content in load_notes():
                self.notes_layout.add_widget(NoteItem(nid, title, content))
        self.dismiss()


class NotesApp(App):
    def build(self):
        init_db()
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        add_btn = Button(text="Add Note", size_hint_y=None, height=40)
        add_btn.bind(on_release=self.open_add_popup)
        root.add_widget(add_btn)

        self.scroll = ScrollView()
        self.notes_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter("height"))
        self.scroll.add_widget(self.notes_layout)
        root.add_widget(self.scroll)

        self.refresh_notes()
        return root

    def refresh_notes(self):
        self.notes_layout.clear_widgets()
        for note_id, title, content in load_notes():
            self.notes_layout.add_widget(NoteItem(note_id, title, content))

    def open_add_popup(self, *args):
        popup = NotePopup(None, "", "", self.notes_layout)
        # Override save to handle new note
        def add_and_close(instance):
            title = popup.title_input.text.strip()
            content = popup.content_input.text.strip()
            if title and content:
                add_note(title, content)
                self.refresh_notes()
            popup.dismiss()

        # Replace the save button