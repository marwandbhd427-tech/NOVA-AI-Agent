import os, tempfile
from project_manager import ProjectManager
from project_brain import ProjectBrain
from dependency_manager import DependencyManager
from version_manager import VersionManager

td=tempfile.mkdtemp(prefix='nova_v7_test_')
pm=ProjectManager(os.path.join(td,'projects'))
pm.create('demo')
pm.write_files('demo', {'main.py':'import json\n\ndef hello():\n    return "ok"\n','helper.py':'class A: pass\n'})
assert pm.check_python('demo')['success']
b=ProjectBrain(pm, os.path.join(td,'brain'))
i=b.scan('demo'); assert 'main.py' in i['files'] and i['functions']>=1
b.add_feature('demo','test-feature'); assert 'test-feature' in b.load('demo')['features']
d=DependencyManager(pm); assert d.scan('demo')==[]
vm=VersionManager(pm); s=vm.create('demo','test'); assert os.path.isdir(s); assert vm.list('demo')
print('NOVA V7 SELF TEST: PASS')
