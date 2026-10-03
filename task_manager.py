import os,json,uuid
from datetime import datetime
FILE=os.path.join(os.environ.get('NOVA_RUNTIME_DIR',os.path.dirname(os.path.abspath(__file__))),'data','tasks.json')
def load():
    os.makedirs(os.path.dirname(FILE),exist_ok=True)
    try:return json.load(open(FILE,encoding='utf-8'))
    except Exception:return []
def save(x):os.makedirs(os.path.dirname(FILE),exist_ok=True);json.dump(x,open(FILE,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
def add(title,priority='normal',due=None):
    x=load();t={'id':str(uuid.uuid4())[:8],'title':title,'priority':priority,'due':due,'done':False,'created_at':datetime.now().isoformat()};x.append(t);save(x);return t
def complete(i):
    x=load()
    for t in x:
        if t['id']==i:t['done']=True;save(x);return t
    return None
def remove(i):
    x=load();y=[t for t in x if t['id']!=i];save(y);return len(x)!=len(y)
def list_tasks(include_done=False):return [t for t in load() if include_done or not t.get('done')]
