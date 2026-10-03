import ast, os, sys
STDLIB=set(getattr(sys,'stdlib_module_names',())) | {'__future__','typing_extensions'}
class DependencyManager:
    def __init__(self,pm): self.pm=pm
    def scan(self,name):
        root=os.path.join(self.pm.base,name); found=set()
        for rel in self.pm.tree(name):
            if not rel.endswith('.py'): continue
            try: tree=ast.parse(open(os.path.join(root,rel),encoding='utf-8').read())
            except Exception: continue
            for n in ast.walk(tree):
                if isinstance(n,ast.Import): found.update(x.name.split('.')[0] for x in n.names)
                elif isinstance(n,ast.ImportFrom) and n.module: found.add(n.module.split('.')[0])
        local={os.path.splitext(os.path.basename(x))[0] for x in self.pm.tree(name) if x.endswith('.py')}
        external=sorted(x for x in found if x not in STDLIB and x not in local and x not in {'main'})
        return external
    def write(self,name):
        deps=self.scan(name); root=os.path.join(self.pm.base,name)
        with open(os.path.join(root,'requirements.txt'),'w',encoding='utf-8') as f:
            f.write('\n'.join(deps)+'\n')
        return deps
