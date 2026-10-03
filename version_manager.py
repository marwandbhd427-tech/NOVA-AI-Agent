import os, time, json
class VersionManager:
    def __init__(self,pm): self.pm=pm
    def create(self,name,label='checkpoint'):
        snap=self.pm.snapshot(name,label+'_'+str(int(time.time()*1000)))
        meta=os.path.join(snap,'.nova_version.json')
        with open(meta,'w',encoding='utf-8') as f: json.dump({'label':label,'time':time.time()},f)
        return snap
    def list(self,name):
        base=os.path.join(self.pm.base,'.snapshots'); out=[]
        if not os.path.isdir(base): return out
        for x in os.listdir(base):
            if x.startswith(name+'__'): out.append(x)
        return sorted(out, key=lambda x: os.path.getmtime(os.path.join(base,x)), reverse=True)
    def rollback_latest(self,name):
        xs=self.list(name)
        if not xs:return False
        return self.pm.restore_snapshot(name,os.path.join(self.pm.base,'.snapshots',xs[0]))
