class ResearchAgent:
    def __init__(self,search,progress=print): self.search=search; self.say=progress
    def research(self,query):
        self.say('🔎 Research Agent: البحث عن معلومات مفيدة...')
        try:return self.search(query)
        except Exception as e:return {'success':False,'error':str(e)}
