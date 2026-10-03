import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class NOVAAndroidApp(App):
    def build(self):
        # All writable NOVA data goes into Android's private app storage.
        os.environ["NOVA_RUNTIME_DIR"] = self.user_data_dir

        self.nova = None
        self._build_ui()

        # Ask for the Groq key before importing NOVA Core so the Core
        # initializes with the key already available.
        key_file = os.path.join(self.user_data_dir, "groq_key.txt")
        if self._read_key(key_file):
            self._load_core()
        else:
            Clock.schedule_once(lambda dt: self._show_key_dialog(), 0.2)

        return self.root

    def _build_ui(self):
        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8),
        )

        self.title_label = Label(
            text="NOVA AI V11.1\nجاري التشغيل...",
            size_hint_y=None,
            height=dp(65),
            font_size=dp(19),
            bold=True,
        )
        root.add_widget(self.title_label)

        self.chat = Label(
            text="NOVA Android\n\n",
            size_hint_y=None,
            halign="left",
            valign="top",
            text_size=(None, None),
        )

        self.scroll = ScrollView(do_scroll_x=False)
        self.scroll.add_widget(self.chat)
        root.add_widget(self.scroll)

        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(6),
        )

        self.input = TextInput(
            hint_text="اكتب طلبك لـ NOVA...",
            multiline=False,
            font_size=dp(16),
        )
        self.send_button = Button(
            text="إرسال",
            size_hint_x=None,
            width=dp(90),
        )
        self.send_button.bind(on_press=self.send_message)
        self.input.bind(on_text_validate=self.send_message)

        bottom.add_widget(self.input)
        bottom.add_widget(self.send_button)
        root.add_widget(bottom)

        self.root = root

    def _read_key(self, path):
        try:
            if not os.path.exists(path):
                return None
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("gsk_"):
                    return line
        except Exception:
            pass
        return None

    def _save_key(self, key):
        path = os.path.join(self.user_data_dir, "groq_key.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(key.strip() + "\n")

    def _show_key_dialog(self):
        box = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        info = Label(
            text="أدخل Groq API Key لتشغيل NOVA AI.\nالمفتاح يحفظ داخل مساحة التطبيق الخاصة."
        )
        key_input = TextInput(
            hint_text="gsk_...",
            password=True,
            multiline=False,
        )

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        save = Button(text="تشغيل NOVA")
        offline = Button(text="متابعة بدون مفتاح")
        buttons.add_widget(save)
        buttons.add_widget(offline)

        box.add_widget(info)
        box.add_widget(key_input)
        box.add_widget(buttons)

        popup = Popup(
            title="إعداد NOVA",
            content=box,
            size_hint=(0.94, 0.48),
            auto_dismiss=False,
        )

        def do_save(_):
            key = key_input.text.strip()
            if not key.startswith("gsk_"):
                info.text = "المفتاح غير صالح. يجب أن يبدأ بـ gsk_"
                return
            self._save_key(key)
            popup.dismiss()
            self._load_core()

        def do_offline(_):
            popup.dismiss()
            self._load_core()

        save.bind(on_press=do_save)
        offline.bind(on_press=do_offline)
        popup.open()

    def _load_core(self):
        try:
            import main as nova_core
            self.nova = nova_core
            self.title_label.text = "NOVA AI V11.1\nجاهز 🧠"
            self.add_message("NOVA", "تم تشغيل NOVA Core بنجاح.")
        except Exception as e:
            self.title_label.text = "NOVA AI V11.1\nخطأ في التشغيل"
            self.add_message("NOVA ERROR", repr(e))

    def send_message(self, *_):
        text = self.input.text.strip()
        if not text or self.nova is None:
            return

        self.input.text = ""
        self.send_button.disabled = True
        self.add_message("أنت", text)

        threading.Thread(
            target=self._worker,
            args=(text,),
            daemon=True,
        ).start()

    def _worker(self, text):
        try:
            answer = self.nova.ask_nova(text)
            if answer == "__EXIT__":
                answer = "تم إيقاف NOVA."
        except Exception as e:
            answer = "NOVA ERROR: " + repr(e)

        Clock.schedule_once(
            lambda dt: self._finish_answer(str(answer)),
            0,
        )

    def _finish_answer(self, answer):
        self.add_message("NOVA", answer)
        self.send_button.disabled = False

    def add_message(self, sender, message):
        self.chat.text += f"{sender}:\n{message}\n\n"
        self.chat.text_size = (self.chat.width, None)
        self.chat.texture_update()
        Clock.schedule_once(
            lambda dt: setattr(self.scroll, "scroll_y", 0),
            0.05,
        )


if __name__ == "__main__":
    NOVAAndroidApp().run()
