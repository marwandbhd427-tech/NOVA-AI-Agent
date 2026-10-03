import ast
import math
import io
import contextlib
import traceback


ALLOWED_MATH = {
    "pi": math.pi,
    "e": math.e,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "abs": abs,
    "round": round,
    "pow": pow,
}


SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "sum": sum,
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
    "enumerate": enumerate,
    "zip": zip,
}


BLOCKED_TEXT = [
    "import os",
    "import subprocess",
    "import shutil",
    "import socket",
    "import sys",
    "from os",
    "from subprocess",
    "from shutil",
    "from socket",
    "from sys",
    "open(",
    "__import__",
    "eval(",
    "exec(",
    "compile(",
]


def calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        allowed_nodes = (
            ast.Expression,
            ast.Constant,
            ast.Num,
            ast.BinOp,
            ast.UnaryOp,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.FloorDiv,
            ast.Mod,
            ast.Pow,
            ast.USub,
            ast.UAdd,
            ast.Call,
            ast.Name,
        )

        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                return {
                    "success": False,
                    "error": f"عملية غير مسموحة: {type(node).__name__}",
                }

            if isinstance(node, ast.Name):
                if node.id not in ALLOWED_MATH:
                    return {
                        "success": False,
                        "error": f"اسم غير مسموح: {node.id}",
                    }

            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    return {
                        "success": False,
                        "error": "استدعاء دالة غير مسموح.",
                    }

                if node.func.id not in ALLOWED_MATH:
                    return {
                        "success": False,
                        "error": f"دالة غير مسموحة: {node.func.id}",
                    }

        result = eval(
            compile(tree, "<calculator>", "eval"),
            {"__builtins__": {}},
            ALLOWED_MATH,
        )

        return {
            "success": True,
            "result": result,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


def _normalize_common_code(code):
    """
    إصلاح بسيط لأخطاء شائعة جداً في النص المولد.
    لا يغير منطق البرنامج عمداً.
    """
    lines = code.splitlines()
    cleaned = []

    for line in lines:
        stripped = line.strip()

        # إذا التصق assert مع print بسبب توليد النموذج
        if "assert " in line and " print(" in line:
            before, after = line.split(" print(", 1)
            indent = line[:len(line) - len(line.lstrip())]

            cleaned.append(before.rstrip())
            cleaned.append(indent + "print(" + after)
        else:
            cleaned.append(line)

    return "\n".join(cleaned)


def test_python_code(code):
    if not isinstance(code, str):
        return {
            "success": False,
            "output": "",
            "error": "الكود ليس نصاً.",
        }

    code = code.strip()

    if not code:
        return {
            "success": False,
            "output": "",
            "error": "الكود فارغ.",
        }

    lowered = code.lower()

    for blocked in BLOCKED_TEXT:
        if blocked.lower() in lowered:
            return {
                "success": False,
                "output": "",
                "error": f"تعليمة غير مسموحة: {blocked}",
            }

    code = _normalize_common_code(code)

    try:
        compiled = compile(
            code,
            "<nova_code>",
            "exec",
        )
    except Exception as error:
        return {
            "success": False,
            "output": "",
            "error": traceback.format_exc(),
        }

    output_buffer = io.StringIO()

    namespace = {
        "__name__": "__main__",
        "__builtins__": SAFE_BUILTINS,
    }

    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(
                compiled,
                namespace,
                namespace,
            )

        return {
            "success": True,
            "output": output_buffer.getvalue(),
            "error": "",
        }

    except Exception:
        return {
            "success": False,
            "output": output_buffer.getvalue(),
            "error": traceback.format_exc(),
        }
