import json,re
class MultiFileAgent:
    def __init__(self,llm,pm):self.llm=llm;self.pm=pm
    def parse(self,text):
        text=text.strip();text=re.sub(r'^```json\s*','',text,flags=re.I);text=re.sub(r'```$','',text).strip()
        try:return json.loads(text)
        except Exception:
            m=re.search(r'\{.*\}',text,re.S)
            if m:return json.loads(m.group(0))
            raise
    def generate_project(self,name,request):
        if not self.llm:return {'success':False,'error':'Language Engine غير متوفر.'}
        prompt='''أنت مهندس مشاريع داخل NOVA. أنشئ مشروع Python متعدد الملفات. أعد JSON فقط بالشكل {"files":{"main.py":"..."},"tests":{"tests/test_main.py":"..."}}. اجعل المشروع قابلاً للاختبار ولا تستخدم os أو subprocess أو socket في الكود المولد. الطلب: '''+request
        data=self.parse(self.llm.ask(prompt));files=data.get('files',{});files.update(data.get('tests',{}));self.pm.write_files(name,files);return {'success':True,'project':name,'files':list(files)}
