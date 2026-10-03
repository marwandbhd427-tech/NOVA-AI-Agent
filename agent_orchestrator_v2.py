class AgentOrchestratorV2:
    """Deterministic state machine around NOVA's existing agents."""
    STATES=('UNDERSTAND','PLAN','SNAPSHOT','EXECUTE','TEST','HEAL','COMMIT','ROLLBACK','REPORT')
    def __init__(self,pm,brain,health,tx,auto,heal,progress=None):
        self.pm=pm;self.brain=brain;self.health=health;self.tx=tx;self.auto=auto;self.heal=heal;self.say=progress or (lambda x:None)
    def _state(self,s): self.say('🤖 Orchestrator: '+s)
    def create(self,request):
        self._state('UNDERSTAND → PLAN')
        result=self.auto.run(request)
        name=result.get('project') if isinstance(result,dict) else None
        if not name:return result
        self._state('VALIDATE')
        health=self.health.analyze(name)
        if result.get('success') and health.get('success'):
            self.brain.remember(name,'orchestrator_build','autonomous build completed')
            self.brain.scan(name)
        result['health']=health
        return result
    def modify(self,name,request):
        if not self.heal:return {'success':False,'error':'healing_unavailable'}
        self._state('SNAPSHOT')
        tx=self.tx.begin(name,'modify')
        try:
            self._state('EXECUTE')
            result=self.heal.edit.modify(request,name)
            self._state('TEST')
            test=self.pm.test(name)
            if not test.get('success'):
                self._state('HEAL')
                healed=self.heal.heal(name,request)
                if not healed.get('success'):
                    self.tx.rollback(tx,'tests failed after modification')
                    return {'success':False,'rolled_back':True,'result':result,'test':test,'healed':healed}
                test=healed.get('test',test)
            self._state('COMMIT'); self.tx.commit(tx,'tests passed')
            self.brain.remember(name,'orchestrator_modify',request);self.brain.scan(name)
            return {'success':True,'result':result,'test':test,'health':self.health.analyze(name)}
        except Exception as e:
            self.tx.rollback(tx,str(e)); return {'success':False,'rolled_back':True,'error':str(e)}
