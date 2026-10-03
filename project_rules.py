import os, json, time
class ProjectRules:
    def __init__(self,base='data/project_rules'):
        self.base=base; os.makedirs(base,exist_ok=True)
    def path(self,name): return os.path.join(self.base,name.replace('..','_').replace('/','_').replace('\\','_')+'.json')
    def load(self,name):
        try:return json.load(open(self.path(name),encoding='utf-8'))
        except Exception:return {'project':name,'rules':[],'updated_at':0}
    def save(self,name,data):
        data['updated_at']=time.time(); json.dump(data,open(self.path(name),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    def add(self,name,rule):
        d=self.load(name); rule=str(rule).strip()
        if rule and rule not in d['rules']: d['rules'].append(rule)
        self.save(name,d); return d['rules']
    def list(self,name): return self.load(name).get('rules',[])
    def text(self,name):
        xs=self.list(name); return '📐 Project Rules\n'+'\n'.join(f'{i+1}. {x}' for i,x in enumerate(xs)) if xs else '📐 لا توجد قواعد محفوظة.'
