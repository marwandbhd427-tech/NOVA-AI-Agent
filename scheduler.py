import os,json,time,threading,uuid
from datetime import datetime,timedelta
FILE=os.path.join(os.environ.get('NOVA_RUNTIME_DIR',os.path.dirname(os.path.abspath(__file__))),'data','scheduler.json')
class Scheduler:
    def __init__(self,callback=None):self.callback=callback;self.jobs=[];self.running=False;self.load()
    def load(self):
        try:self.jobs=json.load(open(FILE,encoding='utf-8'))
        except Exception:self.jobs=[]
    def save(self):os.makedirs(os.path.dirname(FILE),exist_ok=True);json.dump(self.jobs,open(FILE,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    def add_after_seconds(self,seconds,text):
        j={'id':str(uuid.uuid4())[:8],'when':(datetime.now()+timedelta(seconds=float(seconds))).isoformat(),'text':text,'done':False};self.jobs.append(j);self.save();return j
    def remove(self,i):
        old=len(self.jobs);self.jobs=[j for j in self.jobs if j.get('id')!=i];self.save();return old!=len(self.jobs)
    def start(self):
        if self.running:return
        self.running=True;threading.Thread(target=self._loop,daemon=True).start()
    def stop(self):self.running=False
    def _loop(self):
        while self.running:
            now=datetime.now();changed=False
            for j in self.jobs:
                if not j.get('done'):
                    try:due=datetime.fromisoformat(j['when'])
                    except Exception:continue
                    if now>=due:
                        j['done']=True;changed=True
                        if self.callback:
                            try:self.callback(j['text'])
                            except Exception as e:print('Scheduler:',e)
            if changed:self.save()
            time.sleep(1)
    def list(self):return self.jobs[:]
