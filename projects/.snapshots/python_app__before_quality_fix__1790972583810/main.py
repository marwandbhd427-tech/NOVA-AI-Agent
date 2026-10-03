import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DATA_FILE = "notes.json"


class NoteApp:
    def __init__(self):
        # GUI components are created lazily in run()
        self.root = None
        self.notes = {}
        self.load_notes()

    # ---------- Data handling ----------
    def load_notes(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.notes = json.load(f)
            except Exception:
                self.notes = {}

    def save_notes(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            if self.root:
                messagebox.showerror("خطأ", f"فشل في حفظ الملاحظات: {e}")

    # ---------- UI initialization ----------
    def init_ui(self):
        try:
            self.root = tk.Tk()
        except Exception:
            # Environment without Tk support
            self.root = None
            return

        self.root.title("ملاحظات")
        self.root.geometry("600x400")

        # Main frames
        self.left_frame = ttk.Frame(self.root, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Listbox for note titles
        self.note_list = tk.Listbox(self.left_frame, width=30)
        self.note_list.pack(fill=tk.Y, expand=True, padx=5, pady=5)
        self.note_list.bind("<<ListboxSelect>>", self.on_select)

        # Text area for note content
        self.text_area = tk.Text(self.right_frame, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.add_btn = ttk.Button(btn_frame, text="أضف", command=self.add_note)
        self.add_btn.pack(fill=tk.X, pady=2)

        self.del_btn = ttk.Button(btn_frame, text="احذف", command=self.delete_note)
        self.del_btn.pack(fill=tk.X, pady=2)

        self.save_btn = ttk.Button(btn_frame, text="حفظ", command=self.save_current)
        self.save_btn.pack(fill=tk.X, pady=2)

        self.refresh_list()

    # ---------- UI callbacks ----------
    def on_select(self, event):
        if not self.note_list:
            return
        selected = self.note_list.curselection()
        if selected:
            title = self.note_list.get(selected[0])
            content = self.notes.get(title, "")
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)

    def add_note(self):
        if not self.root:
            return
        title = simpledialog.askstring("عنوان", "أدخل عنوان الملاحظة:", parent=self.root)
        if title:
            if title in self.notes:
                messagebox.showwarning("تحذير", "الملاحظة موجودة بالفعل.", parent=self.root)
                return
            self.notes[title] = ""
            self.refresh_list()
            self.note_list.selection_clear(0, tk.END)
            self.note_list.selection_set(tk.END)
            self.on_select(None)

    def delete_note(self):
        if not self.root:
            return
        selected = self.note_list.curselection()
        if not selected:
            messagebox.showinfo("معلومات", "اختر ملاحظة لحذفها.", parent=self.root)
            return
        title = self.note_list.get(selected[0])
        if messagebox.askyesno("تأكيد", f"هل تريد حذف الملاحظة \"{title}\"؟", parent=self.root):
            del self.notes[title]
            self.refresh_list()
            self.text_area.delete(1.0, tk.END)

    def save_current(self):
        if not self.root:
            return
        selected = self.note_list.curselection()
        if not selected:
            messagebox.showinfo("معلومات", "اختر ملاحظة لحفظها.", parent=self.root)
            return
        title = self.note_list.get(selected[0])
        content = self.text_area.get(1.0, tk.END).rstrip()
        self.notes[title] = content
        self.save_notes()
        messagebox.showinfo("تم", "تم حفظ الملاحظة.", parent=self.root)

    # ---------- Helper ----------
    def refresh_list(self):
        if not self.note_list:
            return
        self.note_list.delete(0, tk.END)
        for title in sorted(self.notes.keys()):
            self.note_list.insert(tk.END, title)

    # ---------- Execution ----------
    def run(self):
        self.init_ui()
        if self.root:
            self.root.mainloop()


if __name__ == "__main__":
    app = NoteApp()
    app.run()