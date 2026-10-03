import os, ast, json, sys, time

class ProjectIntelligence:
    def __init__(self, pm):
        self.pm = pm

    def analyze(self, name):
        root = os.path.abspath(os.path.join(self.pm.base, name))
        if not os.path.isdir(root):
            return {"success": False, "error": "project not found"}
        files = self.pm.tree(name)
        py = [f for f in files if f.endswith(".py")]
        info = {"success": True, "name": name, "tree": files, "python": [], "imports": [], "entrypoints": [], "type": self._type(files)}
        imports=set()
        local={os.path.splitext(os.path.basename(f))[0] for f in py}
        for rel in py:
            path=os.path.join(root,rel)
            try:
                text=open(path,encoding="utf-8").read()
                tree=ast.parse(text)
                funcs=[]; classes=[]; imps=[]
                for n in ast.walk(tree):
                    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): funcs.append(n.name)
                    elif isinstance(n,ast.ClassDef): classes.append(n.name)
                    elif isinstance(n,ast.Import):
                        imps += [x.name.split('.')[0] for x in n.names]
                    elif isinstance(n,ast.ImportFrom) and n.module: imps.append(n.module.split('.')[0])
                imports.update(imps)
                info["python"].append({"file":rel,"lines":len(text.splitlines()),"functions":funcs[:30],"classes":classes[:20]})
                if os.path.basename(rel)=="main.py" or "__main__" in text:
                    info["entrypoints"].append(rel)
            except Exception as e:
                info["python"].append({"file":rel,"error":str(e)})
        info["imports"]=sorted(imports)
        stdlib = set(getattr(sys, "stdlib_module_names", ())) | {"__future__","curses","dataclasses","termios","tty","tkinter","select","msvcrt","time","typing"}
        info["requirements"]=[x for x in info["imports"] if x not in stdlib and x not in local]
        return info

    def _type(self, files):
        s=" ".join(files).lower()
        if "snake" in s: return "snake"
        if "pygame" in s: return "pygame"
        if "tkinter" in s: return "tkinter"
        if "flask" in s: return "flask"
        if "discord" in s: return "discord"
        return "python"

    def summary(self,name):
        d=self.analyze(name)
        if not d.get("success"): return str(d)
        return json.dumps(d,ensure_ascii=False,indent=2)[:10000]
