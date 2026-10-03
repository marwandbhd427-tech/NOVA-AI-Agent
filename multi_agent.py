class MultiAgentOrchestrator:
    """Role-based orchestration over the existing NOVA agents, with bounded calls."""
    def __init__(self,engine,auto_agent,edit_agent,brain,progress=print):
        self.engine=engine; self.auto=auto_agent; self.edit=edit_agent; self.brain=brain; self.say=progress
    def _role(self,role,request,context=''):
        if not self.engine:return ''
        prompt=(f'أنت Agent متخصص بدور: {role}.\n'
                'لا تكتب كودًا كاملًا. أعطني نقاطًا عملية مختصرة فقط.\n'
                f'الطلب: {request}\n{context}')
        return self.engine.ask_raw(prompt,max_tokens=700)
    def new_project(self,request):
        # The AutonomousAgent owns the authoritative deterministic plan.
        # Do not spend extra LLM calls generating a second plan that the coder
        # does not actually consume; this also reduces Groq rate-limit risk.
        self.say('🧠 Project Manager: فهم الطلب...')
        self.say('🗺️ Project Planner: بناء الخطة التنفيذية...')
        self.say('💻 Coding Agent: تنفيذ المشروع...')
        result=self.auto.run(request)
        if isinstance(result,dict) and result.get('project'):
            self.brain.remember(result['project'],'created',request); self.brain.scan(result['project'])
        return result
    def modify(self,name,request):
        self.say('🧠 Project Brain: فهم المشروع...')
        info=self.brain.scan(name)
        context='ملفات: '+', '.join(info.get('files',[])[:40])+'\nميزات: '+', '.join(info.get('features',[])[:20])
        self.say('🗺️ Planner Agent: تحديد أقل تغييرات لازمة...')
        self._role('Change Planner',request,context)
        self.say('💻 Coding Agent: تنفيذ التعديل...')
        result=self.edit.modify(request,name) if self.edit else {'success':False,'error':'edit agent unavailable'}
        if isinstance(result,dict) and result.get('success'):
            self.brain.remember(name,'modified',request); self.brain.add_feature(name,request); self.brain.scan(name)
        return result
