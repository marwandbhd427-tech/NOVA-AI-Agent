import json
import re
import time


class UniversalAgent:
    """Natural-language control layer for NOVA.

    It does not replace deterministic tools. It decides when to use them and
    keeps execution separate from the language model.
    """

    def __init__(self, language_engine=None, progress=None):
        self.llm = language_engine
        self.progress = progress or (lambda x: None)

    def say(self, msg):
        try:
            self.progress(str(msg))
        except Exception:
            pass

    @staticmethod
    def _norm(text):
        s = str(text or '').lower().strip()
        s = s.replace('إ', 'ا').replace('أ', 'ا').replace('آ', 'ا')
        return re.sub(r'\s+', ' ', s)

    def classify(self, text):
        """Cheap deterministic intent classification before using the LLM."""
        t = self._norm(text)

        if any(x in t for x in ('انشئ ملف', 'انشاء ملف', 'اعمل ملف', 'اصنع ملف',
                                'create file', 'make file', 'new file', 'انشئ مجلد', 'اعمل مجلد', 'سوي مجلد', 'أنشئ مجلد')):
            return 'filesystem'

        if any(x in t for x in ('اعمل مشروع', 'انشئ مشروع', 'انشاء مشروع', 'اصنع مشروع', 'سوي مشروع',
                                'اعمل لعبة', 'اعمل لي لعبة', 'انشئ لعبة', 'انشئ لي لعبة', 'اصنع لعبة', 'اصنع لي لعبة', 'سوي لعبة', 'طور لعبة',
                                'برمج لعبة', 'اعمل برنامج', 'اعمل لي برنامج', 'انشئ برنامج', 'انشئ لي برنامج', 'اصنع برنامج', 'اصنع لي برنامج', 'سوي برنامج',
                                'برمج برنامج', 'اعمل تطبيق', 'اعمل لي تطبيق', 'انشئ تطبيق', 'انشئ لي تطبيق', 'اصنع تطبيق', 'اصنع لي تطبيق', 'برمج تطبيق', 'برمج لي تطبيق',
                                'انشئ موقع', 'اعمل موقع', 'اصنع موقع', 'برمج موقع',
                                'اكتب لي برنامج', 'اكتب برنامج', 'اكتب لي تطبيق',
                                'create a project', 'build a project', 'make a game',
                                'create a game', 'build an app', 'create a website', 'build a website',
                                'python project')):
            return 'create_project'

        if any(x in t for x in ('شغل المشروع', 'شغل اللعبة', 'شغل البرنامج', 'شغل التطبيق',
                                'run project', 'run the project', 'شغّل المشروع')):
            return 'project_run'

        if any(x in t for x in ('اختبر المشروع', 'اختبر اللعبة', 'اختبر البرنامج',
                                'test project', 'test the project')):
            return 'project_test'

        if any(x in t for x in ('اعرض ملفات المشروع', 'اعرض ملفات', 'شجرة المشروع',
                                'project tree', 'show project files')):
            return 'project_tree'

        if any(x in t for x in ('عدل المشروع', 'عدّل المشروع', 'اصلح المشروع', 'اصلح الكود',
                                'عدل الكود', 'طوّر المشروع', 'طور المشروع', 'غير المشروع',
                                'اضف للمشروع', 'أضف للمشروع', 'fix the project',
                                'modify the project', 'update the project', 'improve the project')):
            return 'modify_project'

        if any(x in t for x in ('اقرا الملف', 'حلل الملف', 'حلل المجلد', 'اقرأ الملف',
                                'read file', 'analyze file', 'analyze folder')):
            return 'file'

        if any(x in t for x in ('ابحث عن', 'ابحث لي', 'دور على', 'فتش عن', 'search for',
                                'look up')):
            return 'search'

        if any(x in t for x in ('تذكر', 'احفظ', 'تعلم ان', 'تعلم أن', 'هل تتذكر',
                                'memory', 'remember')):
            return 'memory'

        if any(x in t for x in ('حالة المشروع','صحة المشروع','project health','project status','health of project')):
            return 'project_health'
        if any(x in t for x in ('اصلح المشروع تلقائيا','اصلح المشروع تلقائي','اصلح المشروع','self heal','self-heal','heal project')):
            return 'project_heal'
        if any(x in t for x in ('جاهز للاندرويد','جاهز للاندرويد','فحص اندرويد','فحص android','pydroid','android readiness')):
            return 'project_android'
        if any(x in t for x in ('ما هي قدراتك','قدرات نوفا','capabilities','nova status','حالة نوفا')):
            return 'nova_status'
        if any(x in t for x in ('اعمل نسخة احتياطية', 'نسخة احتياطية', 'backup project', 'snapshot project')):
            return 'project_snapshot'

        if any(x in t for x in ('ارجع للنسخة', 'تراجع عن التعديل', 'rollback project', 'restore project')):
            return 'project_rollback'

        if any(x in t for x in ('حلل المشروع', 'افهم المشروع', 'خريطة المشروع', 'project analysis', 'project map')):
            return 'project_info'

        if any(x in t for x in ('متطلبات المشروع', 'مكتبات المشروع', 'dependencies', 'requirements')):
            return 'project_deps'

        if any(x in t for x in ('اضف مهمة', 'أضف مهمة', 'ذكرني', 'remind me', 'task')):
            return 'task'

        return 'answer'

    def llm_intent(self, text):
        if not self.llm:
            return None
        prompt = '''You are NOVA's intent classifier. Return ONLY JSON.
Schema: {"intent":"answer|search|create_project|modify_project|file|task|memory","target":"","request":""}
Rules:
- create_project means the user wants NOVA to actually build files/project/game/app/program.
- modify_project means the user wants changes to an existing project.
- file means reading/analyzing/creating ordinary files or folders.
- search means the user explicitly asks to look something up online.
- answer means normal conversation/question.
Do not execute anything. Do not invent missing names.
User: ''' + str(text)
        try:
            raw = self.llm.ask_raw(prompt, max_tokens=220)
            raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', str(raw).strip(), flags=re.I | re.S)
            obj = json.loads(raw)
            if obj.get('intent') in {'answer','search','create_project','modify_project','file','task','memory'}:
                return obj
        except Exception:
            return None
        return None

    def choose(self, text):
        intent = self.classify(text)
        # Deterministic action verbs always win. LLM is only a fallback for
        # ambiguous natural language.
        if intent != 'answer':
            return {'intent': intent, 'target': '', 'request': text, 'source': 'rules'}
        obj = self.llm_intent(text)
        if obj:
            obj['source'] = 'llm'
            return obj
        return {'intent': 'answer', 'target': '', 'request': text, 'source': 'rules'}
