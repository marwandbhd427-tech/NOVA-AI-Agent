import os,sys,subprocess,re,ast

STDLIB=set(getattr(sys, "stdlib_module_names", ())) | {
'__future__','curses','dataclasses','termios','tty','tkinter','time','typing_extensions'
}
class RuntimeAgent:
    def __init__(self,pm,progress=None,timeout=8): self.pm=pm;self.progress=progress or (lambda x:None);self.timeout=timeout
    def say(self,x):
        try:self.progress(x)
        except:pass
    def scan_imports(self,name):
        mods=set();root=os.path.join(self.pm.base,name)
        for b,ds,fs in os.walk(root):
            ds[:]=[d for d in ds if d in ('tests',) or d=='__pycache__']
            for f in fs:
                if not f.endswith('.py') or f.startswith('test_'):continue
                try: tree=ast.parse(open(os.path.join(b,f),encoding='utf-8').read())
                except: continue
                for n in ast.walk(tree):
                    if isinstance(n,ast.Import): mods|={x.name.split('.')[0] for x in n.names}
                    elif isinstance(n,ast.ImportFrom) and n.module: mods.add(n.module.split('.')[0])
        local={os.path.splitext(x)[0] for x in self.pm.tree(name) if x.endswith('.py')}
        return sorted(x for x in mods if x not in STDLIB and x not in local)
    def requirements(self,name):
        deps=self.scan_imports(name);root=os.path.join(self.pm.base,name)
        p=os.path.join(root,'requirements.txt')
        if deps and not os.path.exists(p):
            open(p,'w',encoding='utf-8').write('\n'.join(deps)+'\n')
        return deps
    def import_entry(self,name,entry='main.py'):
        root=os.path.join(self.pm.base,name); path=os.path.join(root,entry)
        if not os.path.isfile(path): return {'status':'missing','output':entry+' not found'}
        try:
            code='import sys; sys.path.insert(0, "."); __import__("'+os.path.splitext(entry)[0]+'")'
            r=subprocess.run([sys.executable,'-c',code],cwd=root,capture_output=True,text=True,timeout=self.timeout,env={**os.environ,'NOVA_AGENT_TEST':'1'})
            out=(r.stdout+'\n'+r.stderr)[-10000:]
            if r.returncode==0: return {'status':'ok','returncode':0,'output':out}
            low=out.lower(); env_like=any(x in low for x in ('no module named','modulenotfounderror','importerror','pygame.error: video','pygame.error: audio','no available video device'))
            return {'status':'runtime_error','returncode':r.returncode,'output':out,'environment_like':env_like}
        except subprocess.TimeoutExpired: return {'status':'timeout','output':'import timed out'}
        except Exception as e: return {'status':'runtime_error','output':str(e)}

    def run_entry(self,name,entry='main.py'):
        root=os.path.join(self.pm.base,name);path=os.path.join(root,entry)
        if not os.path.isfile(path): return {'status':'missing','output':entry+' not found'}
        try:
            r=subprocess.run([sys.executable,entry],cwd=root,capture_output=True,text=True,timeout=self.timeout,env={**os.environ,'NOVA_AGENT_TEST':'1'})
            out=(r.stdout+'\n'+r.stderr)[-10000:]
            if r.returncode==0:
                return {'status':'ok','returncode':0,'output':out}
            low=out.lower()
            env_like=any(x in low for x in (
                'no module named', 'modulenotfounderror', 'importerror',
                'no available video device', 'video system not initialized',
                'no available video device', 'video system not initialized',
                'pygame.error: video', 'pygame.error: audio',
                'tclerror', 'tkinter.tclerror', 'curses.error',
                'termios.error', 'no such device', 'xdg_runtime_dir'
            ))
            return {'status':'runtime_error','returncode':r.returncode,'output':out,'environment_like':env_like}
        except subprocess.TimeoutExpired as e:
            out=((e.stdout or '') if isinstance(e.stdout,str) else '')[-3000:]
            return {'status':'timeout','output':out}
        except Exception as e:return {'status':'runtime_error','output':str(e)}
