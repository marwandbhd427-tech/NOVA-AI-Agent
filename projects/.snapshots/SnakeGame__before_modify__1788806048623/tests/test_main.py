import os,unittest
class TestBuild(unittest.TestCase):
 def test_python_compiles(self):
  root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));n=0
  for base,ds,fs in os.walk(root):
   ds[:]=[d for d in ds if d not in {'tests','__pycache__'}]
   for f in fs:
    if f.endswith('.py'):
     p=os.path.join(base,f)
     with open(p,encoding='utf-8') as h: compile(h.read(),p,'exec')
     n+=1
  self.assertGreater(n,0)
if __name__=='__main__':unittest.main()
