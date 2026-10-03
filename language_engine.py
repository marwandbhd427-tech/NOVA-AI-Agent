import os
from groq import Groq


# ============================================================
#                    NOVA LANGUAGE ENGINE
# ============================================================

MODEL = "openai/gpt-oss-20b"

class RateLimitError(RuntimeError):
    """Groq rate/TPD limit; callers should stop retrying and preserve the project."""
    pass

SYSTEM_PROMPT = """
أنت NOVA، ذكاء اصطناعي شخصي قيد التطوير.

شخصيتك:
- ذكي
- هادئ
- واضح
- ودود
- لا تدعي أنك تعرف شيئاً إذا لم تكن متأكداً
- تحدث مع المستخدم باللغة التي يستخدمها

أنت جزء من نظام أكبر يحتوي على:
- ذاكرة
- Neural Brain
- أدوات
- نظام تعلم

لا تقل للمستخدم أنك مجرد API.
أنت NOVA.

عندما يكون السؤال بسيطاً، أجب باختصار.
عندما يحتاج السؤال إلى شرح، اشرح بشكل واضح ومنظم.
"""


class LanguageEngine:

    def __init__(self, api_key):

        if not api_key:
            raise ValueError(
                "لم يتم العثور على GROQ API KEY"
            )

        self.client = Groq(
            api_key=api_key
        )

        self.history = []


    def ask(self, user_text, memory_context=""):
        return self._request(user_text, memory_context, keep_history=True, max_tokens=4096)

    def ask_raw(self, user_text, max_tokens=2600):
        """Small stateless request for agents. Avoids conversation history/TPM growth."""
        return self._request(user_text, "", keep_history=False, max_tokens=max_tokens)

    def _request(self, user_text, memory_context="", keep_history=True, max_tokens=4096):

        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]

        # --------------------------------------------
        # Memory context
        # --------------------------------------------

        if memory_context:

            messages.append({

                "role": "system",

                "content":
                    "معلومات من ذاكرة NOVA:\n"
                    + memory_context

            })


        # --------------------------------------------
        # Previous conversation
        # --------------------------------------------

        if keep_history:
            messages.extend(self.history[-6:])


        # --------------------------------------------
        # Current user
        # --------------------------------------------

        messages.append({

            "role": "user",

            "content": user_text

        })


        # --------------------------------------------
        # API
        # --------------------------------------------

        try:
            response = (
                self.client
                .chat
                .completions
                .create(
                    model=MODEL,
                    messages=messages,
                    temperature=0.7,
                    max_completion_tokens=max_tokens
                )
            )
        except Exception as e:
            text = str(e)
            low = text.lower()
            if ("429" in low or "rate_limit" in low or "rate limit" in low or
                "tokens per day" in low or "tpd" in low):
                raise RateLimitError("Groq Rate Limit: تم الوصول إلى حد الاستخدام اليومي/المؤقت. أوقف الإصلاحات مؤقتًا ثم أعد المحاولة لاحقًا.") from e
            raise


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        # --------------------------------------------
        # Save context
        # --------------------------------------------

        if not keep_history:
            return answer

        self.history.append({

            "role": "user",

            "content": user_text

        })

        self.history.append({

            "role": "assistant",

            "content": answer

        })


        # Keep history small
        if len(self.history) > 20:

            self.history = self.history[-20:]


        return answer