import json, os, time

class ExecutionContext:
    """Small persistent context for NOVA's active project and recent actions."""
    def __init__(self, path='.nova_context.json'):
        self.path=os.path.abspath(path)
        self.data={'active_project':None,'last_intent':None,'last_request':None,'last_result':None,'history':[]}
        self.load()
    def load(self):
        try:
            if os.path.isfile(self.path):
                d=json.load(open(self.path,encoding='utf-8'))
                if isinstance(d,dict): self.data.update(d)
        except Exception: pass
    def save(self):
        try:
            tmp=self.path+'.tmp'
            with open(tmp,'w',encoding='utf-8') as f: json.dump(self.data,f,ensure_ascii=False,indent=2)
            os.replace(tmp,self.path)
        except Exception: pass
    def set_project(self,name): self.data['active_project']=name; self.save()
    def project(self): return self.data.get('active_project')
    def record(self,intent,request,result=None):
        self.data.update({'last_intent':intent,'last_request':request,'last_result':result})
        h=self.data.setdefault('history',[])
        h.append({'time':time.time(),'intent':intent,'request':str(request)[:500],'ok':bool(result is not None and (not isinstance(result,dict) or result.get('success',True)))})
        self.data['history']=h[-30:]
        self.save()

class AuditLog:
    def __init__(self,path='data/agent_audit.jsonl'):
        self.path=os.path.abspath(path); os.makedirs(os.path.dirname(self.path),exist_ok=True)
    def write(self,action,request,result=None):
        row={'time':time.time(),'action':action,'request':str(request)[:1000]}
        if isinstance(result,dict): row['success']=result.get('success'); row['project']=result.get('project')
        elif result is not None: row['result']=str(result)[:1000]
        try:
            with open(self.path,'a',encoding='utf-8') as f: f.write(json.dumps(row,ensure_ascii=False)+'\n')
        except Exception: pass
