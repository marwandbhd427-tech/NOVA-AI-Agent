import os
import unittest

class TestProjectSyntax(unittest.TestCase):
    def test_python_files_compile(self):
        root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        checked=0
        for base, _, names in os.walk(root):
            if '__pycache__' in base or os.path.basename(base) == 'tests':
                continue
            for name in names:
                if name.endswith('.py'):
                    path=os.path.join(base,name)
                    source=open(path, encoding='utf-8').read()
                    compile(source, path, 'exec')
                    checked += 1
        self.assertGreaterEqual(checked, 1)

if __name__ == '__main__':
    unittest.main()
