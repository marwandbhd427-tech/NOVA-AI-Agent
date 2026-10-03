import re

from tools import calculate

from extra_tools import (
    weather,
    currency,
    convert_units,
    random_number,
)


class ToolRouter:

    def __init__(self, language_engine, code_agent, memory):
        self.language_engine = language_engine
        self.code_agent = code_agent
        self.memory = memory

    # ==========================================
    # DETECT TOOL
    # ==========================================

    def detect_tool(self, text):

        t = text.lower().strip()

        # ------------------------------
        # CODE
        # ------------------------------

        coding_words = [
            "اكتب كود",
            "اكتب لي كود",
            "اعمل كود",
            "اعمل لي كود",
            "اكتب برنامج",
            "اكتب لي برنامج",
            "اعمل برنامج",
            "اعمل لي برنامج",
            "برمج",
            "برمج لي",
            "كود بايثون",
            "بايثون",
            "python",
            "python code",
            "debug",
            "debug code",
            "صلح الكود",
            "اصلح الكود",
            "صحح الكود",
            "اختبر الكود",
            "اختبر البرنامج",
            "برنامج بايثون",
        ]

        if any(word in t for word in coding_words):
            return "code"

        # ------------------------------
        # WEATHER
        # ------------------------------

        weather_words = [
            "الطقس",
            "الجو",
            "حالة الطقس",
            "حاله الطقس",
            "درجة الحرارة",
            "درجه الحراره",
            "توقعات الطقس",
            "weather",
            "forecast",
            "temperature",
        ]

        if any(word in t for word in weather_words):
            return "weather"

        # ------------------------------
        # CURRENCY
        # ------------------------------

        currency_words = [
            "تحويل العملة",
            "تحويل العملات",
            "سعر الصرف",
            "صرف",
            "exchange rate",
            "دولار الى",
            "دولار إلى",
            "يورو الى",
            "يورو إلى",
            "درهم الى",
            "درهم إلى",
            "usd",
            "eur",
            "mad",
        ]

        if any(word in t for word in currency_words):
            return "currency"

        # ------------------------------
        # UNITS
        # ------------------------------

        unit_words = [
            "حول",
            "تحويل",
            "كم متر",
            "كم كيلو",
            "كيلومتر",
            "كيلومترات",
            "كيلوغرام",
            "كيلوغرامات",
            "سنتيمتر",
            "متر",
            "درجة مئوية",
            "فهرنهايت",
            "celsius",
            "fahrenheit",
        ]

        if any(word in t for word in unit_words):

            unit_names = [
                "متر",
                "كيلومتر",
                "كم",
                "سم",
                "سنتيمتر",
                "مم",
                "مليمتر",
                "كيلو",
                "كيلوغرام",
                "كغ",
                "غرام",
                "درجة",
                "مئوية",
                "فهرنهايت",
                "celsius",
                "fahrenheit",
            ]

            if any(unit in t for unit in unit_names):
                return "units"

        # ------------------------------
        # RANDOM
        # ------------------------------

        random_words = [
            "رقم عشوائي",
            "عدد عشوائي",
            "اختار رقم",
            "اختر رقم",
            "رقم من",
            "random number",
            "random",
        ]

        if any(word in t for word in random_words):
            return "random"

        # ------------------------------
        # CALCULATOR
        # ------------------------------

        calculator_words = [
            "احسب",
            "احسب لي",
            "كم يساوي",
            "ما ناتج",
            "عملية حسابية",
            "calculate",
        ]

        if any(word in t for word in calculator_words):
            return "calculator"

        # ------------------------------
        # MEMORY
        # ------------------------------

        memory_words = [
            "هل تتذكر",
            "تتذكر",
            "ماذا تعرف عني",
            "ماذا تعرف عن",
            "احفظ",
            "تعلم أن",
            "تعلم ان",
            "ذاكرة",
            "memory",
        ]

        if any(word in t for word in memory_words):
            return "memory"

        # ------------------------------
        # LANGUAGE
        # ------------------------------

        return "language"

    # ==========================================
    # CALCULATOR
    # ==========================================

    def extract_expression(self, text):

        expression = text.strip()

        replacements = [
            "احسب لي",
            "احسب",
            "كم يساوي",
            "ما ناتج",
            "calculate",
            "Calculate",
        ]

        for word in replacements:
            expression = expression.replace(
                word,
                ""
            )

        expression = expression.strip()

        expression = expression.replace(
            "×",
            "*"
        )

        expression = expression.replace(
            "÷",
            "/"
        )

        expression = expression.replace(
            "^",
            "**"
        )

        return expression

    def run_calculator(self, text):

        expression = self.extract_expression(
            text
        )

        if not expression:

            return {
                "success": False,
                "error": "لم أجد عملية حسابية."
            }

        return calculate(
            expression
        )

    # ==========================================
    # WEATHER
    # ==========================================

    def extract_city(self, text):

        patterns = [

            r"(?:في|ب|مدينة)\s+([^\؟\?\!\.,،]+)",

            r"(?:طقس|الطقس|الجو)\s+([^\؟\?\!\.,،]+)",

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                city = match.group(1).strip()

                endings = [
                    " غدا",
                    " غدًا",
                    " غداً",
                    " اليوم",
                    " الآن",
                    " بكرا",
                ]

                for ending in endings:

                    city = city.replace(
                        ending,
                        ""
                    ).strip()

                if city:
                    return city

        return None

    def run_weather(self, text):

        city = self.extract_city(
            text
        )

        if not city:

            return {
                "success": False,
                "needs_city": True,
                "error":
                    "اكتب اسم المدينة، مثلاً: "
                    "ما طقس الرباط غداً؟"
            }

        return weather(
            city
        )

    # ==========================================
    # CURRENCY
    # ==========================================

    def currency_code(self, value):

        mapping = {

            "دولار": "USD",
            "دولارات": "USD",
            "usd": "USD",

            "يورو": "EUR",
            "eur": "EUR",

            "درهم": "MAD",
            "درهم مغربي": "MAD",
            "mad": "MAD",

            "جنيه": "GBP",
            "جنيه استرليني": "GBP",
            "gbp": "GBP",
        }

        return mapping.get(
            value.lower(),
            value.upper()
        )

    def run_currency(self, text):

        pattern = (
            r"([0-9]+(?:\.[0-9]+)?)\s*"
            r"(دولار|دولارات|usd|"
            r"يورو|eur|درهم|mad|"
            r"جنيه|gbp)"
            r"\s*(?:الى|إلى|ل|to)\s*"
            r"(دولار|usd|يورو|eur|"
            r"درهم|mad|جنيه|gbp)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:

            return {
                "success": False,
                "error":
                    "مثال: حول 100 دولار إلى درهم."
            }

        amount = match.group(1)

        from_currency = self.currency_code(
            match.group(2)
        )

        to_currency = self.currency_code(
            match.group(3)
        )

        return currency(
            amount,
            from_currency,
            to_currency
        )

    # ==========================================
    # UNITS
    # ==========================================

    def run_units(self, text):

        pattern = (
            r"([0-9]+(?:\.[0-9]+)?)\s*"
            r"([A-Za-z°]+|متر|كيلومتر|كم|سم|"
            r"سنتيمتر|مم|مليمتر|كغ|كيلوغرام|"
            r"غرام|درجة|مئوية|فهرنهايت)"
            r"\s*(?:الى|إلى|ل|to)\s*"
            r"([A-Za-z°]+|متر|كيلومتر|كم|سم|"
            r"سنتيمتر|مم|مليمتر|كغ|كيلوغرام|"
            r"غرام|درجة|مئوية|فهرنهايت)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:

            return {
                "success": False,
                "error":
                    "مثال: حول 5 كيلومتر إلى متر."
            }

        return convert_units(
            match.group(1),
            match.group(2),
            match.group(3)
        )

    # ==========================================
    # RANDOM
    # ==========================================

    def run_random(self, text):

        numbers = re.findall(
            r"-?\d+",
            text
        )

        if len(numbers) >= 2:

            return random_number(
                numbers[0],
                numbers[1]
            )

        if len(numbers) == 1:

            return random_number(
                1,
                numbers[0]
            )

        return random_number()

    # ==========================================
    # MAIN ROUTER
    # ==========================================

    def route(self, text):

        tool = self.detect_tool(
            text
        )

        if tool == "code":

            return {
                "tool": "code",
                "result":
                    self.code_agent.build_and_test(
                        text
                    )
            }

        if tool == "calculator":

            return {
                "tool": "calculator",
                "result":
                    self.run_calculator(
                        text
                    )
            }

        if tool == "weather":

            return {
                "tool": "weather",
                "result":
                    self.run_weather(
                        text
                    )
            }

        if tool == "currency":

            return {
                "tool": "currency",
                "result":
                    self.run_currency(
                        text
                    )
            }

        if tool == "units":

            return {
                "tool": "units",
                "result":
                    self.run_units(
                        text
                    )
            }

        if tool == "random":

            return {
                "tool": "random",
                "result":
                    self.run_random(
                        text
                    )
            }

        if tool == "memory":

            return {
                "tool": "memory",
                "result": self.memory
            }

        return {
            "tool": "language",
            "result": None
        }