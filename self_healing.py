import re

class SelfHealingEngine:
    def __init__(self,pm,runtime=None,edit_agent=None,health=None,progress=None):
        self.pm=pm; self.runtime=runtime; self.edit=edit_agent; self.health=health; self.say=progress or (lambda x:None)
    def heal(self,name,request='fix project'):
        if not self.edit:return {'success':False,'error':'edit_agent_unavailable'}
        before=self.pm.snapshot(name,'before_heal')
        test=self.pm.test(name)
        if test.get('success'):
            return {'success':True,'already_healthy':True,'test':test}
        out=str(test.get('output',''))
        self.say('🩺 Self-Healing: تحليل سبب الفشل...')
        result=self.edit.modify((request+'\nError:\n'+out[-5000:]).strip(),name)
        after=self.pm.test(name)
        if after.get('success'):
            return {'success':True,'repaired':True,'result':result,'test':after}
        self.pm.restore_snapshot(name,before)
        return {'success':False,'repaired':False,'rolled_back':True,'result':result,'test':after}
