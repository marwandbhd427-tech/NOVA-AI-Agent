import os, ast, json, time

class ProjectHealth:
    def __init__(self,pm,brain=None,runtime=None,deps=None): self.pm=pm;self.brain=brain;self.runtime=runtime;self.deps=deps
    def analyze(self,name):
        root=os.path.join(self.pm.base,name)
        if not os.path.isdir(root): return {'success':False,'error':'project_not_found'}
        tree=self.pm.tree(name); py=[x for x in tree if x.endswith('.py')]
        compile_report=self.pm.check_python(name)
        tests=self.pm.run_tests(name)
        deps=self.deps.scan(name) if self.deps else []
        todo=0; lines=0; syntax=0
        for rel in py:
            p=os.path.join(root,rel)
            try:
                text=open(p,encoding='utf-8').read(); lines+=len(text.splitlines()); todo+=sum(text.lower().count(x) for x in ('todo','fixme'))
                ast.parse(text,filename=rel)
            except Exception: syntax+=1
        score=100
        score-=min(35,len(compile_report.get('errors',[]))*20)
        if tests.get('success') is False: score-=25
        score-=min(15,len(deps)*2)
        score-=min(10,todo)
        score=max(0,score)
        return {'success':True,'project':name,'score':score,'grade':'A' if score>=90 else 'B' if score>=75 else 'C' if score>=60 else 'D',
                'files':len(tree),'python_files':len(py),'lines':lines,'tests_ok':tests.get('success',False),'syntax_errors':syntax,
                'compile':compile_report,'test_output':tests.get('output',''),'external_dependencies':deps,'todo_count':todo,'timestamp':time.time()}
    def text(self,name):
        r=self.analyze(name)
        if not r.get('success'): return '❌ '+str(r.get('error'))
        return (f"🏥 Project Health: {name}\n📊 Score: {r['score']}/100 ({r['grade']})\n"
                f"📁 Files: {r['files']} | Python: {r['python_files']} | Lines: {r['lines']}\n"
                f"🧪 Tests: {'PASS' if r['tests_ok'] else 'FAIL'} | Syntax errors: {r['syntax_errors']}\n"
                f"📦 External deps: {len(r['external_dependencies'])} | TODO/FIXME: {r['todo_count']}")
