class ProjectTemplates:
    TEMPLATES={
      'python_cli':['main.py','tests/test_main.py'],
      'pygame_game':['main.py','game.py','tests/test_main.py'],
      'kivy_android':['main.py','app.py','tests/test_main.py'],
      'web_app':['index.html','style.css','script.js'],
      'fastapi_api':['main.py','requirements.txt','tests/test_main.py'],
      'flask_app':['app.py','requirements.txt','templates/index.html'],
      'ai_project':['main.py','config.py','memory.py','tests/test_main.py'],
    }
    def list(self): return self.TEMPLATES
    def get(self,name): return self.TEMPLATES.get(name)
    def text(self): return '\n'.join(f'• {k}: '+', '.join(v) for k,v in self.TEMPLATES.items())
