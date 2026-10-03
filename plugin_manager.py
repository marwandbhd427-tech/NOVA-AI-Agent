import os, importlib.util
BASE=os.path.dirname(os.path.abspath(__file__)); DIR=os.path.join(BASE,'plugins')
def ensure():os.makedirs(DIR,exist_ok=True)
def list_plugins():
    ensure();return [f[:-3] for f in sorted(os.listdir(DIR)) if f.endswith('.py') and not f.startswith('_')]
def load_plugins():
    ensure(); loaded=[]
    for name in list_plugins():
        try:
            p=os.path.join(DIR,name+'.py'); spec=importlib.util.spec_from_file_location('nova_plugin_'+name,p); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); loaded.append(mod)
        except Exception as e:print('Plugin warning:',name,e)
    return loaded
def plugin_status():return {'plugins':list_plugins(),'count':len(list_plugins())}
