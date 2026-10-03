from universal_agent import UniversalAgent

CASES = {
    'اعمل لعبة ثعبان ببايثون': 'create_project',
    'انشئ ملف notes.txt': 'filesystem',
    'شغل المشروع': 'project_run',
    'اختبر المشروع': 'project_test',
    'اعرض ملفات المشروع': 'project_tree',
    'عدل المشروع واضف نظام حفظ': 'modify_project',
    'ابحث عن اخر تحديث لماينكرافت': 'search',
    'ما هو الفرق بين list و tuple في بايثون؟': 'answer',
}

for text, expected in CASES.items():
    got = UniversalAgent().choose(text)['intent']
    assert got == expected, (text, got, expected)

print('NOVA V9 Universal tests: PASS')
