from tools import test_python_code


class CodeAgent:

    def __init__(self, language_engine):
        self.language_engine = language_engine

    def generate_code(self, request):
        prompt = f"""
أنت Code Agent داخل NOVA.

طلب المستخدم الحالي:
{request}

مهم جداً:
- افهم الطلب الحالي فقط.
- لا تستخدم أي طلب سابق.
- لا تعيد استخدام كود سابق إلا إذا كان ضرورياً.
- أنشئ برنامجاً يطابق الطلب الحالي.
- إذا طلب المستخدم اختبار البرنامج، أضف اختباراً حقيقياً.
- إذا طلب المستخدم إصلاح خطأ، تعامل مع الخطأ المطلوب.
- لا تستخدم if __name__ == "__main__": إلا إذا كان ضرورياً.
- الأفضل أن تستدعي الدوال المطلوبة مباشرة في نهاية الكود.
- لا تستخدم os أو subprocess أو shutil أو socket أو sys.
- لا تستخدم الإنترنت أو ملفات النظام.
- لا تستخدم Markdown.
- أعد كود Python فقط.
"""
        return (self.language_engine.ask_raw(prompt, max_tokens=2800) if hasattr(self.language_engine, "ask_raw") else self.language_engine.ask(prompt))

    def clean_code(self, code):
        code = code.strip()

        if "```" in code:
            parts = code.split("```")

            if len(parts) >= 2:
                code = parts[1].strip()

                if code.lower().startswith("python"):
                    code = code[6:].strip()

        return code.strip()

    def fix_code(self, code, error):
        prompt = f"""
أنت تقوم بإصلاح كود Python داخل NOVA.

طلب المستخدم الأصلي:
يجب أن يبقى هدف البرنامج كما طلبه المستخدم.

الكود الحالي:
{code}

خطأ الاختبار:
{error}

المطلوب:
- أصلح الخطأ الحقيقي.
- حافظ على وظيفة البرنامج.
- لا تستبدل البرنامج بمثال آخر.
- أعد الكود الكامل.
- أضف اختباراً مناسباً إذا كان المستخدم طلب الاختبار.
- لا تستخدم if __name__ == "__main__": إلا إذا كان ضرورياً.
- لا تستخدم os أو subprocess أو shutil أو socket أو sys.
- لا تستخدم الإنترنت أو ملفات النظام.
- لا تضع Markdown.
- أعد الكود فقط.
"""
        fixed = (self.language_engine.ask_raw(prompt, max_tokens=2800) if hasattr(self.language_engine, "ask_raw") else self.language_engine.ask(prompt))
        return self.clean_code(fixed)

    def run(self, code):
        return test_python_code(code)

    def build_and_test(self, request, max_attempts=3):
        print()
        print("💻 Code Agent")
        print("=" * 60)
        print("🧠 Generating code...")

        code = self.generate_code(request)
        code = self.clean_code(code)

        if not code:
            return {
                "success": False,
                "code": "",
                "output": "",
                "error": "لم يتم توليد كود.",
                "attempts": 0,
            }

        for attempt in range(1, max_attempts + 1):
            print()
            print(f"🧪 Test attempt {attempt}/{max_attempts}")

            result = self.run(code)

            if result["success"]:
                print("✅ Code executed successfully!")

                return {
                    "success": True,
                    "code": code,
                    "output": result["output"],
                    "attempts": attempt,
                }

            print("❌ Error detected.")

            if attempt >= max_attempts:
                return {
                    "success": False,
                    "code": code,
                    "output": result["output"],
                    "error": result["error"],
                    "attempts": attempt,
                }

            print("🔧 NOVA is repairing the code...")

            code = self.fix_code(
                code,
                result["error"],
            )

        return {
            "success": False,
            "code": code,
            "output": "",
            "error": "Unknown error",
            "attempts": max_attempts,
        }
