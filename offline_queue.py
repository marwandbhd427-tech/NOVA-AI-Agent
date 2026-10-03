import os,json,time

class OfflineQueue:
    def __init__(self,path='data/agent_queue.json'):
        self.path=path; os.makedirs(os.path.dirname(path) or '.',exist_ok=True)
    def _load(self):
        try:
            with open(self.path,encoding='utf-8') as f:return json.load(f)
        except Exception:return []
    def _save(self,x):
        with open(self.path,'w',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
    def add(self,kind,project,request):
        q=self._load(); item={'id':int(time.time()*1000),'kind':kind,'project':project,'request':request,'created_at':time.time(),'status':'pending'}; q.append(item); self._save(q); return item
    def list(self): return self._load()
    def pending(self): return [x for x in self._load() if x.get('status')=='pending']
    def mark(self,item_id,status,result=''):
        q=self._load()
        for x in q:
            if x.get('id')==item_id:x['status']=status;x['result']=str(result);x['updated_at']=time.time()
        self._save(q)
    def clear_done(self):
        q=[x for x in self._load() if x.get('status')=='pending']; self._save(q); return len(q)
