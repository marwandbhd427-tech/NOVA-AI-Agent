import re

class WorkspaceAgent:
    """High-level project continuation layer. Keeps decisions deterministic and LLM calls bounded."""
    def __init__(self, orchestrator, pm, brain, memory, queue, progress=print):
        self.orch=orchestrator; self.pm=pm; self.brain=brain; self.memory=memory; self.queue=queue; self.say=progress
    def latest(self):
        ps=self.pm.list_projects()
        if not ps:return None
        import os
        return max(ps,key=lambda n: os.path.getmtime(os.path.join(self.pm.base,n)))

    def resolve(self, request='', preferred=None):
        """Resolve a project name from an explicit mention, then preferred, then latest."""
        ps=self.pm.list_projects()
        if not ps:return None
        text=str(request or '').lower()
        for name in ps:
            if name.lower() in text:return name
        return preferred if preferred in ps else self.latest()
    def continue_project(self, request, name=None):
        name=name or self.latest()
        if not name:return {'success':False,'error':'لا يوجد مشروع سابق.'}
        self.say('🧠 Workspace: استعادة ذاكرة المشروع...')
        info=self.brain.scan(name)
        mem=self.memory.summary(name)
        self.say(f"   📂 {len(info.get('files',[]))} ملف | 🧠 {len(mem.get('features',[]))} ميزة محفوظة")
        self.memory.event(name,'command',request)
        return self.orch.modify(name,request)
    def new_project(self,request):
        return self.orch.new_project(request)
    def queue_request(self,request,name=None):
        name=name or self.latest() or 'pending_project'
        return self.queue.add('modify',name,request)
    def queue_status(self): return self.queue.list()
