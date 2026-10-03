import os, sys, platform, re

class AndroidProjectAgent:
    def __init__(self,pm,deps=None): self.pm=pm; self.deps=deps
    def analyze(self,name):
        root=os.path.join(self.pm.base,name)
        files=self.pm.tree(name) if os.path.isdir(root) else []
        text='\n'.join(self.pm.read_project(name,max_chars=12000).values()) if files else ''
        imports=(self.deps.scan(name) if self.deps else [])
        pydroid=[]
        if 'pygame' in text.lower(): pydroid.append('Pygame: يحتاج SDL/display/audio مناسبين للهاتف')
        if 'kivy' in text.lower(): pydroid.append('Kivy: مناسب نسبيًا لتطبيقات Android')
        if 'tkinter' in text.lower(): pydroid.append('Tkinter: غير مناسب كخيار APK أساسي')
        if not pydroid:pydroid.append('لم يتم اكتشاف إطار واجهة رئيسي')
        build_files=[x for x in files if x.lower() in ('buildozer.spec','pyproject.toml','android.txt')]
        return {'success':bool(files),'project':name,'python':sys.version.split()[0],'platform':platform.platform(),
                'files':len(files),'dependencies':imports,'android_build_files':build_files,'pydroid_notes':pydroid,
                'apk_ready':bool(build_files),'recommendation':'Kivy/Buildozer أو BeeWare حسب نوع المشروع' if not build_files else 'يوجد إعداد Android؛ راجع المتطلبات قبل البناء'}
    def text(self,name):
        r=self.analyze(name)
        if not r.get('success'):return '❌ المشروع غير موجود.'
        return ('📱 Android/Pydroid Intelligence\n'
                f"Project: {name}\nPython: {r['python']}\nFiles: {r['files']}\n"
                f"APK config: {'YES' if r['apk_ready'] else 'NO'}\n"
                'Dependencies: '+(', '.join(r['dependencies']) or 'none')+'\n'
                'Notes: '+' | '.join(r['pydroid_notes'])+'\n'
                'Recommendation: '+r['recommendation'])
