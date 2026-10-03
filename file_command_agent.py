import os
import re


class FileCommandAgent:
    """Small deterministic filesystem actions with a sandboxed workspace."""
    def __init__(self, base=None):
        if base is None:
            base=os.path.join(os.environ.get('NOVA_RUNTIME_DIR', os.getcwd()), 'workspace_files')
        self.base=os.path.abspath(base)
        os.makedirs(self.base, exist_ok=True)

    def _safe(self, rel):
        rel=str(rel or '').strip().replace('\\','/')
        rel=re.sub(r'^[/]+','',rel)
        p=os.path.abspath(os.path.join(self.base,rel))
        if not p.startswith(self.base+os.sep):
            raise ValueError('مسار غير آمن')
        return p

    def create_file(self, rel, content=''):
        p=self._safe(rel)
        os.makedirs(os.path.dirname(p),exist_ok=True)
        with open(p,'w',encoding='utf-8') as f:f.write(str(content))
        return {'success':True,'path':os.path.relpath(p,self.base),'size':len(str(content))}

    def create_folder(self, rel):
        p=self._safe(rel);os.makedirs(p,exist_ok=True)
        return {'success':True,'path':os.path.relpath(p,self.base)}
