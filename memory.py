import os
import json
from datetime import datetime


# ============================================================
#                    NOVA MEMORY SYSTEM
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    os.environ.get("NOVA_RUNTIME_DIR", BASE_DIR),
    "data"
)

MEMORY_FILE = os.path.join(
    DATA_DIR,
    "memory.json"
)


# ============================================================
# 📁 CREATE DATA DIRECTORY
# ============================================================

def ensure_data_directory():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )


# ============================================================
# 💾 DEFAULT MEMORY
# ============================================================

def default_memory():

    return {
        "facts": [],
        "conversations": []
    }


# ============================================================
# 📥 LOAD MEMORY
# ============================================================

def load_memory():

    ensure_data_directory()

    if not os.path.exists(
        MEMORY_FILE
    ):

        memory = default_memory()

        save_memory(memory)

        return memory


    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            memory = json.load(file)


        if not isinstance(
            memory,
            dict
        ):

            memory = default_memory()


        # Migrate old/corrupted memory formats safely.
        # Older NOVA versions could store facts as a dict.
        # V6.x uses a list of {key, value, ...} objects.
        facts = memory.get("facts", [])
        if isinstance(facts, dict):
            migrated = []
            for key, value in facts.items():
                migrated.append({
                    "key": str(key),
                    "value": value,
                    "created_at": datetime.now().isoformat()
                })
            memory["facts"] = migrated
        elif not isinstance(facts, list):
            memory["facts"] = []

        conversations = memory.get("conversations", [])
        if not isinstance(conversations, list):
            memory["conversations"] = []


        return memory


    except Exception as error:

        print(
            "⚠️ تعذر قراءة الذاكرة:"
        )

        print(error)

        return default_memory()


# ============================================================
# 💾 SAVE MEMORY
# ============================================================

def save_memory(memory):

    ensure_data_directory()

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                ensure_ascii=False,
                indent=4
            )

        return True


    except Exception as error:

        print(
            "⚠️ تعذر حفظ الذاكرة:"
        )

        print(error)

        return False


# ============================================================
# 🧠 ADD MEMORY
# ============================================================

def add_memory(
    memory,
    key,
    value
):

    if not isinstance(
        memory,
        dict
    ):

        return False


    if "facts" not in memory:

        memory["facts"] = []


    # --------------------------------------------------------
    # إذا كانت المعلومة موجودة، نقوم بتحديثها
    # --------------------------------------------------------

    for fact in memory["facts"]:

        if isinstance(
            fact,
            dict
        ):

            if fact.get("key") == key:

                fact["value"] = value

                fact["updated_at"] = (
                    datetime.now().isoformat()
                )

                return True


    # --------------------------------------------------------
    # إضافة معلومة جديدة
    # --------------------------------------------------------

    memory["facts"].append({

        "key": key,

        "value": value,

        "created_at": (
            datetime.now().isoformat()
        )

    })


    return True


# ============================================================
# 🔎 GET MEMORY
# ============================================================

def get_memory(
    memory,
    key
):

    if not isinstance(
        memory,
        dict
    ):

        return None


    facts = memory.get(
        "facts",
        []
    )


    for fact in facts:

        if isinstance(
            fact,
            dict
        ):

            if fact.get("key") == key:

                return fact.get(
                    "value"
                )


    return None


# ============================================================
# 🧠 GET ALL FACTS
# ============================================================

def get_facts(memory):

    if not isinstance(
        memory,
        dict
    ):

        return []


    return memory.get(
        "facts",
        []
    )


# ============================================================
# 🗣️ SAVE CONVERSATION
# ============================================================

def save_conversation(
    memory,
    user_text,
    assistant_text
):

    if not isinstance(
        memory,
        dict
    ):

        return False


    if "conversations" not in memory:

        memory["conversations"] = []


    memory["conversations"].append({

        "user": user_text,

        "assistant": assistant_text,

        "timestamp": (
            datetime.now().isoformat()
        )

    })


    # --------------------------------------------------------
    # نحتفظ بآخر 100 محادثة فقط
    # --------------------------------------------------------

    if len(
        memory["conversations"]
    ) > 100:

        memory["conversations"] = (
            memory["conversations"][-100:]
        )


    return True


# ============================================================
# 🧹 CLEAR MEMORY
# ============================================================

def clear_memory():

    memory = default_memory()

    save_memory(memory)

    return memory


# ============================================================
# 📊 MEMORY STATUS
# ============================================================

def memory_status(memory):

    if not isinstance(
        memory,
        dict
    ):

        return {
            "facts": 0,
            "conversations": 0
        }


    return {

        "facts": len(
            memory.get(
                "facts",
                []
            )
        ),

        "conversations": len(
            memory.get(
                "conversations",
                []
            )
        )

    }