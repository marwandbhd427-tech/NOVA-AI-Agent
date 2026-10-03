NOVA V7.0.0 — AI DEVELOPMENT PLATFORM

يحافظ هذا الإصدار على NOVA V6.6.5 ويضيف:
- Project Brain: خريطة وذاكرة مستمرة لكل مشروع.
- Multi-Agent Orchestrator: أدوار Architect/Planner/QA/Coding فوق الوكلاء الحاليين.
- Dependency Manager: تحليل imports وإنشاء requirements.txt.
- Version Manager: checkpoints ونسخ المشروع وrollback.
- Project Dashboard: تقرير سريع عن الملفات والكلاسات والدوال والاعتماديات والإصدارات.
- Natural-language project continuation: تعديل آخر مشروع بدل إنشاء مشروع جديد.
- تحسين عرض عدد الملفات الحقيقي.

تشغيل:
python main.py

أوامر جديدة:
project brain NAME
project dashboard NAME
project deps NAME
project deps write NAME
project checkpoint NAME
project versions NAME
project rollback NAME
