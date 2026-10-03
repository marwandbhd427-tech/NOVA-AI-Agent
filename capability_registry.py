import json, os, time

class CapabilityRegistry:
    def __init__(self, path='data/capabilities.json'):
        self.path=path; os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        self.items={}
        self._load()
        if not self.items:
            self.register_defaults()
            self.save()
    def _load(self):
        try:
            with open(self.path,encoding='utf-8') as f: self.items=json.load(f)
        except Exception: self.items={}
    def save(self):
        with open(self.path,'w',encoding='utf-8') as f: json.dump(self.items,f,ensure_ascii=False,indent=2)
    def register(self,name,description,inputs=None,outputs=None,risk='low',enabled=True):
        self.items[name]={'name':name,'description':description,'inputs':inputs or [],'outputs':outputs or [],'risk':risk,'enabled':enabled,'updated_at':time.time()}
    def register_defaults(self):
        defaults=[
            ('project_create','Create a project',['request'],['project'],'medium'),
            ('project_modify','Modify an existing project',['project','request'],['patch'],'medium'),
            ('project_test','Run compile and tests',['project'],['test_report'],'low'),
            ('project_run','Run project entry point',['project'],['runtime_report'],'medium'),
            ('project_snapshot','Create rollback point',['project'],['snapshot'],'low'),
            ('project_rollback','Restore a rollback point',['project'],['project'],'high'),
            ('project_health','Analyze project health',['project'],['health_report'],'low'),
            ('project_research','Research with evidence',['question'],['evidence'],'low'),
            ('filesystem','Read/write workspace files',['path'],['file_result'],'medium'),
            ('android_intelligence','Analyze Android/Pydroid readiness',['project'],['android_report'],'low'),
        ]
        for x in defaults:self.register(*x)
    def get(self,name): return self.items.get(name)
    def list(self): return [self.items[k] for k in sorted(self.items)]
    def summary(self):
        return {'count':len(self.items),'enabled':sum(bool(x.get('enabled')) for x in self.items.values()),'capabilities':sorted(self.items)}
