import os,subprocess,sys,traceback,shutil,time
class ProjectManager:
    def __init__(self,base=None):
        if base is None:
            base=os.path.join(os.environ.get('NOVA_RUNTIME_DIR', os.getcwd()), 'projects')
        self.base=os.path.abspath(base);os.makedirs(self.base,exist_ok=True);os.makedirs(os.path.join(self.base,".snapshots"),exist_ok=True)
    def list_projects(self):return [d for d in sorted(os.listdir(self.base)) if d != '.snapshots' and os.path.isdir(os.path.join(self.base,d))]
    def create(self,name):
        p=os.path.join(self.base,name);os.makedirs(os.path.join(p,'tests'),exist_ok=True);return p
    def write_files(self,name,files):
        root=os.path.join(self.base,name);os.makedirs(root,exist_ok=True);root=os.path.abspath(root)
        for rel,content in files.items():
            p=os.path.abspath(os.path.join(root,rel))
            if not p.startswith(root+os.sep):raise ValueError('مسار غير آمن')
            os.makedirs(os.path.dirname(p),exist_ok=True);open(p,'w',encoding='utf-8').write(content)
        return root
    def read_project(self,name,max_chars=50000):
        root=os.path.abspath(os.path.join(self.base,name))
        if not os.path.isdir(root): return {}
        out={}
        for b,ds,fs in os.walk(root):
            ds[:]=[d for d in ds if d not in {'.git','__pycache__'}]
            for f in fs:
                rel=os.path.relpath(os.path.join(b,f),root)
                if f.endswith(('.py','.txt','.md','.json','.toml','.cfg')):
                    try:
                        text=open(os.path.join(b,f),encoding='utf-8').read()
                        out[rel]=text[:max_chars]
                    except Exception: pass
        return out
    def tree(self,name):
        root=os.path.join(self.base,name);out=[]
        for b,ds,fs in os.walk(root):
            ds[:]=[d for d in ds if d not in {'.git','__pycache__'}]
            for f in fs:out.append(os.path.relpath(os.path.join(b,f),root))
        return out
    def check_python(self,name):
        root=os.path.join(self.base,name);errors=[];count=0
        for b,ds,fs in os.walk(root):
            ds[:]=[d for d in ds if d not in {'.git','__pycache__'}]
            for f in fs:
                if f.endswith('.py'):
                    count+=1;p=os.path.join(b,f)
                    try:compile(open(p,encoding='utf-8').read(),p,'exec')
                    except Exception:errors.append({'file':os.path.relpath(p,root),'error':traceback.format_exc()})
        return {'success':not errors,'files_checked':count,'errors':errors}
    def run_tests(self,name,timeout=15):
        root=os.path.join(self.base,name)
        if not os.path.isdir(os.path.join(root,'tests')):return {'success':True,'output':'لا يوجد tests.'}
        try:
            r=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=root,capture_output=True,text=True,timeout=timeout)
            return {'success':r.returncode==0,'output':(r.stdout+'\n'+r.stderr)[-12000:]}
        except Exception as e:return {'success':False,'output':str(e)}
    def snapshot(self,name,label="snap"):
        root=os.path.join(self.base,name); snap=os.path.join(self.base,".snapshots",name+"__"+label+"__"+str(int(time.time()*1000))); shutil.copytree(root,snap,ignore=shutil.ignore_patterns("__pycache__")); return snap
    def restore_snapshot(self,name,snap):
        root=os.path.join(self.base,name)
        if not snap or not os.path.isdir(snap): return False
        tmp=root+"__restore"; shutil.copytree(snap,tmp,ignore=shutil.ignore_patterns("__pycache__")); shutil.rmtree(root,ignore_errors=True); os.replace(tmp,root); return True
    def test(self,name):
        s=self.check_python(name)
        return s if not s['success'] else self.run_tests(name)
