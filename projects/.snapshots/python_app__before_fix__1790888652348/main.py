import json
import os
import uuid
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

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
        if content is not None:
            note.content = content
        self._save()
        return note

    def delete_note(self, note_id):
        if note_id in self.notes:
            del self.notes[note_id]
            self._save()
        else:
            raise KeyError("Note not found")

    def get_note(self, note_id):
        return self.notes.get(note_id)

    def list_notes(self):
        return list(self.notes.values())


# ---------- GUI Application ----------
class NoteApp(tk.Tk):
    def __init__(self, manager):
        super().__init__()
        self.title("ملاحظات")
        self.geometry("600x400")
        self.manager = manager

        # Left frame for list
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.note_listbox = tk.Listbox(left_frame, width=30)
        self.note_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.note_listbox.bind("<<ListboxSelect>>", self.on_select)

        add_btn = ttk.Button(left_frame, text="إضافة", command=self.add_note)
        add_btn.pack(side=tk.TOP, fill=tk.X, pady=2)

        edit_btn = ttk.Button(left_frame, text="تعديل", command=self.edit_note)
        edit_btn.pack(side=tk.TOP, fill=tk.X, pady=2)

        delete_btn = ttk.Button(left_frame, text="حذف", command=self.delete_note)
        delete_btn.pack(side=tk.TOP, fill=tk.X, pady=2)

        # Right frame for content
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.content_text = tk.Text(right_frame)
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Save button
        save_btn = ttk.Button(right_frame, text="حفظ", command=self.save_content)
        save_btn.pack(side=tk.BOTTOM, fill=tk.X)

        self.refresh_list()

    def refresh_list(self):
        self.note_listbox.delete(0, tk.END)
        for note in self.manager.list_notes():
            self.note_listbox.insert(tk.END, f"{note.title} ({note.id})")

    def get_selected_note_id(self):
        selection = self.note_listbox.curselection()
        if not selection:
            return None
        text = self.note_listbox.get(selection[0])
        # Extract ID from text
        if "(" in text and text.endswith(")"):
            return text.split("(")[-1][:-1]
        return None

    def on_select(self, event):
        note_id = self.get_selected_note_id()
        if note_id:
            note = self.manager.get_note(note_id)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, note.content)

    def add_note(self):
        title = simpledialog.askstring("عنوان", "أدخل عنوان الملاحظة:", parent=self)
        if title is None:
            return
        content = simpledialog.askstring("محتوى", "أدخل محتوى الملاحظة:", parent=self)
        if content is None:
            content = ""
        self.manager.add_note(title, content)
        self.refresh_list()

    def edit_note(self):
        note_id = self.get_selected_note_id()
        if not note_id:
            messagebox.showwarning("تحذير", "اختر ملاحظة لتعديلها", parent=self)
            return
        note = self.manager.get_note(note_id)
        new_title = simpledialog.askstring("عنوان", "أدخل عنوان جديد:", initialvalue=note.title, parent=self)
        if new_title is None:
            return
        new_content = simpledialog.askstring("محتوى", "أدخل محتوى جديد:", initialvalue=note.content, parent=self)
        if new_content is None:
            new_content = ""
        self.manager.edit_note(note_id, title=new_title, content=new_content)
        self.refresh_list()
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, new_content)

    def delete_note(self):
        note_id = self.get_selected_note_id()
        if not note_id:
            messagebox.showwarning("تحذير", "اختر ملاحظة لحذفها", parent=self)
            return
        if messagebox.askyesno("تأكيد", "هل أنت متأكد أنك تريد حذف الملاحظة؟", parent=self):
            self.manager.delete_note(note_id)
            self.refresh_list()
            self.content_text.delete(1.0, tk.END)

    def save_content(self):
        note_id = self.get_selected_note_id()
        if not note_id:
            messagebox.showwarning("تحذير", "اختر ملاحظة لحفظ محتواها", parent=self)
            return
        content = self.content_text.get(1.0, tk.END).rstrip()
        self.manager.edit_note(note_id, content=content)
        messagebox.showinfo("نجاح", "تم حفظ الملاحظة", parent=self)


# ---------- Entry Point ----------
def main():
    manager = NoteManager()
    app = NoteApp(manager)
    app.mainloop()


if __name__ == "__main__":
    main()