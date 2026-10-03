import os,json,time

class ProjectMemory:
    def __init__(self, base='data/project_memory'):
        self.base=base; os.makedirs(base,exist_ok=True)
    def _safe(self,name): return name.replace('..','_').replace('/','_').replace('\\','_')
    def path(self,name): return os.path.join(self.base,self._safe(name)+'.json')
    def load(self,name):
        try:
            with open(self.path(name),encoding='utf-8') as f:return json.load(f)
        except Exception:
            return {'project':name,'goals':[],'features':[],'decisions':[],'commands':[],'errors':[],'sessions':[],'updated_at':0}
    def save(self,name,data):
        data['project']=name; data['updated_at']=time.time()
        with open(self.path(name),'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    def event(self,name,event,details=''):
        d=self.load(name); d.setdefault('sessions',[]).append({'time':time.time(),'event':event,'details':details}); d['sessions']=d['sessions'][-50:]; self.save(name,d)
    def feature(self,name,feature):
        d=self.load(name); arr=d.setdefault('features',[])
        if feature not in arr: arr.append(feature)
        self.save(name,d)
    def error(self,name,error):
        d=self.load(name); d.setdefault('errors',[]).append({'time':time.time(),'error':error}); d['errors']=d['errors'][-30:]; self.save(name,d)
    def summary(self,name):
        d=self.load(name)
        return {'features':d.get('features',[]),'goals':d.get('goals',[]),'decisions':d.get('decisions',[]),'recent':d.get('sessions',[])[-8:],'errors':d.get('errors',[])[-5:]}
