class QAAgent:
    def __init__(self,pm,runtime=None,progress=print): self.pm=pm; self.runtime=runtime; self.say=progress
    def check(self,name):
        self.say('🧪 QA Agent: فحص syntax والاختبارات...')
        result=self.pm.test(name)
        if not result.get('success'): return {'success':False,'stage':'tests','result':result}
        runtime=None
        if self.runtime:
            runtime=self.runtime.run_entry(name)
            if runtime.get('status')=='runtime_error' and not runtime.get('environment_like'):
                return {'success':False,'stage':'runtime','result':runtime}
        return {'success':True,'tests':result,'runtime':runtime}
