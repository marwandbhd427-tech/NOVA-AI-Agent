NOVA V5.2 - Neural Brain Fix

استبدل داخل مجلد NOVA:
- neural_brain.py
- main.py
- tools.py
- code_agent.py

التحسين الرئيسي:
Neural Brain أصبح يملك intent جديد باسم coding، مع أولوية للتعرف على طلبات البرمجة قبل calculator/memory وغيرها.

أمثلة:
اكتب برنامج بايثون... -> coding
صلح الكود -> coding
اختبر البرنامج -> coding
احسب 25 * 4 -> calculator
هل تتذكر... -> memory
من أنت؟ -> identity
كم الساعة؟ -> time
مرحبا -> greeting

ملاحظة:
لا تحتاج لحذف neural_model.npz. الملف الجديد يستخدم النموذج الموجود، ويضع طبقة تعرف مباشرة للأوامر المعروفة حتى لا تعتمد هذه الأوامر على تنبؤ عشوائي من النموذج القديم.
