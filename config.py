import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.environ.get("NOVA_RUNTIME_DIR", BASE_DIR)
os.makedirs(RUNTIME_DIR, exist_ok=True)
KEY_FILE = os.path.join(RUNTIME_DIR, "groq_key.txt")


def get_groq_key():

    # ==========================================
    # إذا كان الملف غير موجود، أنشئه
    # ==========================================

    if not os.path.exists(KEY_FILE):

        with open(
            KEY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "# ضع مفتاح Groq هنا\n"
                "# مثال:\n"
                "# gsk_xxxxxxxxxxxxxxxxx\n"
            )

        print()
        print("📄 تم إنشاء ملف:")
        print("   groq_key.txt")
        print()
        print("🔑 افتح الملف وضع Groq API Key بداخله.")
        print()

        return None


    # ==========================================
    # قراءة المفتاح
    # ==========================================

    try:

        with open(
            KEY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()


        for line in lines:

            line = line.strip()

            # تجاهل التعليقات والأسطر الفارغة

            if not line:
                continue

            if line.startswith("#"):
                continue

            if line.startswith("gsk_"):

                return line


        return None


    except Exception as error:

        print(
            "⚠️ خطأ أثناء قراءة API Key:"
        )

        print(error)

        return None