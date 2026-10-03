import os, time, json

class TransactionEngine:
    """Lightweight transaction wrapper for project mutations."""
    def __init__(self, pm, audit=None): self.pm=pm; self.audit=audit
    def begin(self,name,label='transaction'):
        snap=self.pm.snapshot(name,label+'_'+str(int(time.time()*1000)))
        return {'project':name,'snapshot':snap,'started_at':time.time(),'status':'active'}
    def commit(self,tx,details=''):
        tx['status']='committed'; tx['committed_at']=time.time(); tx['details']=details; return tx
    def rollback(self,tx,reason=''):
        ok=self.pm.restore_snapshot(tx.get('project'),tx.get('snapshot'))
        tx['status']='rolled_back' if ok else 'rollback_failed'; tx['reason']=reason; tx['rolled_back_at']=time.time(); return tx
    def guard(self,name,operation,validator=None):
        tx=self.begin(name,operation)
        try:
            result=operation() if callable(operation) else None
            valid=True if validator is None else bool(validator(result))
            if valid:return self.commit(tx,'validation passed'),result
            return self.rollback(tx,'validation failed'),result
        except Exception as e:
            self.rollback(tx,str(e)); raise
