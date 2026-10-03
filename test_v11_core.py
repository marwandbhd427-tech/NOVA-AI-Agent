import os, tempfile, unittest
from project_manager import ProjectManager
from project_brain import ProjectBrain
from dependency_manager import DependencyManager
from project_health import ProjectHealth
from capability_registry import CapabilityRegistry
from transaction_engine import TransactionEngine
from android_agent import AndroidProjectAgent

class V11CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.mkdtemp(); self.pm=ProjectManager(os.path.join(self.tmp,'projects'))
    def test_capabilities(self):
        c=CapabilityRegistry(os.path.join(self.tmp,'caps.json')); self.assertGreater(c.summary()['count'],5)
    def test_health_and_android(self):
        self.pm.create('demo'); self.pm.write_files('demo',{'main.py':'print("ok")','tests/test_main.py':'import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n'})
        h=ProjectHealth(self.pm,ProjectBrain(self.pm),None,DependencyManager(self.pm)).analyze('demo'); self.assertTrue(h['success']); self.assertTrue(h['tests_ok'])
        a=AndroidProjectAgent(self.pm,DependencyManager(self.pm)).analyze('demo'); self.assertTrue(a['success'])
    def test_transaction_rollback(self):
        self.pm.create('demo'); self.pm.write_files('demo',{'main.py':'A=1'})
        tx=TransactionEngine(self.pm).begin('demo','t'); self.pm.write_files('demo',{'main.py':'A=2'}); TransactionEngine(self.pm).rollback(tx,'test')
        self.assertEqual(open(os.path.join(self.pm.base,'demo','main.py'),encoding='utf-8').read(),'A=1')
if __name__=='__main__': unittest.main()
