import os
import re
import numpy as np


MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "neural_model.npz")


INTENTS = [
    "greeting",
    "identity",
    "time",
    "calculator",
    "learning",
    "memory",
    "help",
    "coding",
]


TRAINING_DATA = {
    "greeting": [
        "مرحبا", "اهلا", "أهلا", "السلام عليكم", "صباح الخير",
        "مساء الخير", "كيف حالك", "hello", "hi", "hey"
    ],
    "identity": [
        "من أنت", "من انت", "ما اسمك", "اسمك ماذا",
        "من تكون", "what are you", "who are you"
    ],
    "time": [
        "كم الساعة", "الساعة كم", "ما الوقت", "الوقت الآن",
        "كم الوقت", "what time is it"
    ],
    "calculator": [
        "احسب", "كم يساوي", "ما ناتج", "عملية حسابية",
        "calculate", "calculate this", "احسب لي"
    ],
    "learning": [
        "تعلم أن", "تعلم ان", "تعلم معلومة", "تعلم",
        "خزن هذه المعلومة", "learn this"
    ],
    "memory": [
        "هل تتذكر", "تتذكر", "ماذا تعرف عني", "ماذا تعرف عن",
        "ما الذي تتذكره", "ذكرني", "ذاكرة", "memory"
    ],
    "help": [
        "ساعدني", "مساعدة", "ماذا تستطيع", "الاوامر",
        "الأوامر", "help", "كيف استخدمك"
    ],
    "coding": [
        "اكتب كود", "اكتب لي كود", "اعمل كود", "اعمل لي كود",
        "اكتب برنامج", "اكتب لي برنامج", "اعمل برنامج",
        "اعمل لي برنامج", "برمج", "برمج لي", "كود بايثون",
        "كود", "بايثون", "python", "python code", "debug",
        "debug code", "صلح الكود", "اصلح الكود", "صحح الكود",
        "اختبر الكود", "اختبر البرنامج", "أنشئ برنامج",
        "انشئ برنامج", "برنامج بايثون"
    ],
}


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, output_size) * 0.1
        self.b2 = np.zeros(output_size)

    def forward(self, x):
        z1 = np.dot(x, self.W1) + self.b1
        a1 = np.maximum(0, z1)
        z2 = np.dot(a1, self.W2) + self.b2

        z2 = z2 - np.max(z2, axis=-1, keepdims=True)
        exp_z = np.exp(z2)
        return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

    def predict(self, x):
        return self.forward(x)


def _features(text):
    text = text.lower().strip()
    vector = np.zeros(256, dtype=float)

    for i, char in enumerate(text[:256]):
        vector[i] = (ord(char) % 257) / 257.0

    return vector


def _keyword_intent(text):
    t = text.lower().strip()

    # coding has highest priority because programming requests
    # can contain words such as "احسب" or "اختبر".
    coding_words = [
        "اكتب كود", "اكتب لي كود", "اعمل كود", "اعمل لي كود",
        "اكتب برنامج", "اكتب لي برنامج", "اعمل برنامج",
        "اعمل لي برنامج", "برمج", "كود بايثون", "بايثون",
        "python", "python code", "debug", "صلح الكود",
        "اصلح الكود", "صحح الكود", "اختبر الكود",
        "اختبر البرنامج", "برنامج بايثون", "أنشئ برنامج",
        "انشئ برنامج",
    ]
    if any(word in t for word in coding_words):
        return "coding", 0.99

    calculator_words = [
        "احسب", "كم يساوي", "ما ناتج", "عملية حسابية",
        "calculate",
    ]
    if any(word in t for word in calculator_words):
        return "calculator", 0.97

    memory_words = [
        "هل تتذكر", "تتذكر", "ماذا تعرف عني", "ماذا تعرف عن",
        "ما الذي تتذكره", "ذكرني", "ذاكرة",
    ]
    if any(word in t for word in memory_words):
        return "memory", 0.97

    learning_words = [
        "تعلم أن", "تعلم ان", "تعلم معلومة",
        "خزن هذه المعلومة", "احفظ هذه المعلومة",
    ]
    if any(word in t for word in learning_words):
        return "learning", 0.97

    identity_words = [
        "من أنت", "من انت", "ما اسمك", "من تكون",
        "what are you", "who are you",
    ]
    if any(word in t for word in identity_words):
        return "identity", 0.97

    time_words = [
        "كم الساعة", "الساعة كم", "ما الوقت",
        "الوقت الآن", "كم الوقت", "what time is it",
    ]
    if any(word in t for word in time_words):
        return "time", 0.97

    help_words = [
        "ساعدني", "مساعدة", "ماذا تستطيع",
        "الأوامر", "الاوامر", "help", "كيف استخدمك",
    ]
    if any(word in t for word in help_words):
        return "help", 0.97

    greeting_words = [
        "مرحبا", "اهلا", "أهلا", "السلام عليكم",
        "صباح الخير", "مساء الخير", "كيف حالك",
        "hello", "hi", "hey",
    ]
    if any(word in t for word in greeting_words):
        return "greeting", 0.97

    return None


def create_brain():
    brain = NeuralNetwork(
        input_size=256,
        hidden_size=64,
        output_size=len(INTENTS),
    )

    if os.path.exists(MODEL_PATH):
        try:
            data = np.load(MODEL_PATH)
            if (
                "W1" in data and "b1" in data and
                "W2" in data and "b2" in data and
                data["W2"].shape[1] == len(INTENTS)
            ):
                brain.W1 = data["W1"]
                brain.b1 = data["b1"]
                brain.W2 = data["W2"]
                brain.b2 = data["b2"]
                print("🧠 Neural model loaded.")
                return brain
        except Exception:
            pass

    print("🧠 Neural model loaded.")
    return brain


def predict_intent(model, text):
    # Deterministic high-confidence routing for known commands.
    # This corrects cases where the old trained model is uncertain.
    keyword_result = _keyword_intent(text)
    if keyword_result:
        return keyword_result

    x = _features(text).reshape(1, -1)
    probabilities = model.predict(x)[0]

    index = int(np.argmax(probabilities))
    confidence = float(probabilities[index])

    return INTENTS[index], confidence
