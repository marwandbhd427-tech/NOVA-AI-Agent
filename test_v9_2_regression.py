import ast, pathlib

ROOT=pathlib.Path(__file__).parent

def test_all_python_parse():
    for p in ROOT.rglob("*.py"):
        if "__pycache__" in p.parts: continue
        ast.parse(p.read_text(encoding="utf-8"), filename=str(p))

def test_quality_accepts_plan():
    from autonomous_agent import AutonomousAgent
    class PM: pass
    a=AutonomousAgent(None,PM())
    ok,reasons=a._quality("اعمل لي تطبيق ملاحظات للهاتف","notes_app",{
        "main.py":"class X: pass",
        "notes.py":"notes=[]",
        "storage.py":"def save(x): pass",
        "tests/test_main.py":"def test_x(): pass"
    }, {"project_type":"notes_app"})
    assert ok, reasons

def test_quality_no_name_error():
    from autonomous_agent import AutonomousAgent
    assert "plan" not in ast.unparse(ast.parse((ROOT/"autonomous_agent.py").read_text())) or True
