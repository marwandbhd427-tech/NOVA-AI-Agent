import os, json, ast, time

class ProjectBrain:
    """Persistent per-project map/memory. Deterministic and lightweight."""
    def __init__(self, pm, base='data/project_brain'):
        self.pm=pm; self.base=base; os.makedirs(base, exist_ok=True)
    def path(self,name):
        safe=name.replace('..','_').replace('/','_').replace('\\','_')
        return os.path.join(self.base, safe+'.json')
    def load(self,name):
        try:
            with open(self.path(name),encoding='utf-8') as f:return json.load(f)
        except Exception:return {'project':name,'features':[],'decisions':[],'history':[]}
    def save(self,name,data):
        data['updated_at']=time.time()
        with open(self.path(name),'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    def scan(self,name):
        root=os.path.join(self.pm.base,name); data=self.load(name)
        files=self.pm.tree(name); py=[]; funcs=0; classes=0; imports=set(); entry=[]
        for rel in files:
            if not rel.endswith('.py'): continue
            py.append(rel); p=os.path.join(root,rel)
            try:
                tree=ast.parse(open(p,encoding='utf-8').read(),filename=rel)
                funcs+=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(tree))
                classes+=sum(isinstance(n,ast.ClassDef) for n in ast.walk(tree))
                for n in ast.walk(tree):
                    if isinstance(n,ast.Import): imports.update(a.name.split('.')[0] for a in n.names)
                    elif isinstance(n,ast.ImportFrom) and n.module: imports.add(n.module.split('.')[0])
                if rel=='main.py' or any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='main' for n in tree.body): entry.append(rel)
            except Exception: pass
        data.update({'project':name,'files':files,'python_files':py,'functions':funcs,'classes':classes,'imports':sorted(imports),'entrypoints':entry or (['main.py'] if 'main.py' in files else []),'project_type':self._type(files,imports)})
        self.save(name,data); return data
    def _type(self,files,imports):
        s=' '.join(files).lower()+' '+' '.join(imports).lower()
        if 'pygame' in s or 'game' in s:return 'game'
        if 'flask' in s or 'fastapi' in s:return 'web'
        if 'tkinter' in s:return 'desktop'
        return 'python'
    def remember(self,name,event,details=''):
        d=self.load(name); d.setdefault('history',[]).append({'time':time.time(),'event':event,'details':details}); d['history']=d['history'][-30:]; self.save(name,d)
    def add_feature(self,name,feature):
        d=self.load(name); f=d.setdefault('features',[])
        if feature not in f:f.append(feature)
        self.save(name,d)
    def report(self,name):
        return self.scan(name)
