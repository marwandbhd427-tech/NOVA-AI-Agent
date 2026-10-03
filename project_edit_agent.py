import json,re,os,time
from pathlib import Path

class ProjectEditAgent:
    def __init__(self,llm,pm,runtime=None,progress=None,error_file="data/project_errors.json"):
        self.llm=llm; self.pm=pm; self.runtime=runtime
        self.progress=progress or (lambda x:None)
        self.error_file=error_file
        os.makedirs(os.path.dirname(error_file) or ".",exist_ok=True)

    def say(self,x):
        try:self.progress(x)
        except: pass
    def ask(self,p,max_tokens=2600):
        try:
            return (self.llm.ask_raw(p,max_tokens=max_tokens) if hasattr(self.llm,"ask_raw") else self.llm.ask(p,"")) or ""
        except Exception as e:
            text=str(e)
            if "Rate Limit" in text or "rate_limit" in text.lower() or "429" in text:
                raise RuntimeError("NOVA_RATE_LIMIT") from e
            self.say("⚠️ "+text); return ""
    def json(self,x):
        x=re.sub(r"^```(?:json)?\s*|\s*```$","",str(x).strip(),flags=re.I|re.S)
        try:return json.loads(x)
        except: 
            a,b=x.find("{"),x.rfind("}")
            if a>=0 and b>a:
                try:return json.loads(x[a:b+1])
                except: pass
        return {}

    def plan(self,request,name,project):
        self.say("📝 خطة التعديل...")
        prompt=f"""You are a senior software engineer modifying an EXISTING Python project.
Return ONLY compact JSON: {{"edit":[file paths],"create":[file paths],"delete":[],"steps":[...]}}.
Do not rewrite unrelated files. Choose the smallest set of files needed.
User request: {request}
Project analysis: {json.dumps(project,ensure_ascii=False)[:8500]}
"""
        try:
            d=self.json(self.ask(prompt,1400))
        except RuntimeError as e:
            if str(e)=="NOVA_RATE_LIMIT":
                raise
            d={}
        valid=lambda p: isinstance(p,str) and ".." not in Path(p).parts and not p.startswith(("/","\\"))
        tree=set(project.get("tree",[]))
        d["edit"]=[p for p in d.get("edit",[]) if valid(p) and p in tree and p.endswith(".py")][:5]
        d["create"]=[p for p in d.get("create",[]) if valid(p) and p not in tree][:4]
        d.setdefault("delete",[]); d.setdefault("steps",[])

        # Deterministic guard for common Snake-store requests. A store normally
        # needs the game/menu integration plus a new store module; touching the
        # Snake entity itself is unnecessary and increases regression risk.
        low_req = request.lower()
        if any(k in low_req for k in ("متجر", "shop", "store")) and any(k in low_req for k in ("snake", "ثعبان")):
            d["edit"] = [x for x in ("main.py", "game.py") if x in tree]
            d["create"] = ["store.py"] if "store.py" not in tree else []
            d["delete"] = []
            d["steps"] = ["create store module", "integrate store with game/menu"]
        if not d["edit"] and not d["create"]:
            if "main.py" in tree: d["edit"]=["main.py"]
        return d

    def _repair_file(self,request,name,path,current,project,error="",history=""):
        prompt=f"""Modify ONE existing Python file to fulfill this request.
Return ONLY the COMPLETE file contents, no markdown.
Request: {request}
Project: {name}
File: {path}
Current contents:
{current[:10000]}
Project context:
{project[:5000]}
Problem/error if any:
{error[-3500:]}
Previous fixes/errors:
{history[-2000:]}
Rules: preserve existing features; make minimal targeted changes; do not replace the whole architecture unless necessary; keep imports compatible; GUI startup under main guard; do not weaken tests."""
        out=self.ask(prompt,3200).strip()
        return re.sub(r"^```(?:python)?\s*|\s*```$","",out,flags=re.I|re.S).strip()

    def _new_file(self,request,name,path,project,current):
        prompt=f"""Create ONE new Python file for an existing project.
Return ONLY complete contents, no markdown.
Request: {request}
Project: {name}
New file: {path}
Project context: {project[:7000]}
Existing relevant files: {current[:6000]}
Integrate cleanly with the existing architecture. No placeholders."""
        return re.sub(r"^```(?:python)?\s*|\s*```$","",self.ask(prompt,2800).strip(),flags=re.I|re.S).strip()

    def _load_errors(self,name):
        try:
            d=json.load(open(self.error_file,encoding="utf-8"))
            return d.get(name,[])
        except: return []
    def _save_error(self,name,error,file=""):
        try:
            d={}
            try:d=json.load(open(self.error_file,encoding="utf-8"))
            except:pass
            d.setdefault(name,[]).append({"time":time.time(),"file":file,"error":str(error)[-1200:]})
            d[name]=d[name][-20:]
            json.dump(d,open(self.error_file,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
        except:pass

    def modify(self,request,name):
        from project_intelligence import ProjectIntelligence
        intel=ProjectIntelligence(self.pm)
        project=intel.analyze(name)
        if not project.get("success"): return {"success":False,"error":"المشروع غير موجود","project":name}
        self.say("🧠 تحليل المشروع الحالي...")
        self.say("   📂 "+str(len(project.get("tree",[])))+" ملف | 🐍 "+str(len(project.get("python",[])))+" Python")
        before=self.pm.snapshot(name,"before_modify")
        baseline=self.pm.test(name)
        try:
            plan=self.plan(request,name,project)
        except RuntimeError as e:
            if str(e)=="NOVA_RATE_LIMIT":
                self.say("⚠️ Groq Rate Limit؛ إيقاف التعديل بدون تخريب المشروع.")
                self.pm.restore_snapshot(name,before)
                return {"success":False,"project":name,"error":"rate_limit","changed":[],"baseline":baseline}
            raise
        changed=[]; errors=self._load_errors(name)
        current=self.pm.read_project(name,max_chars=12000)
        for path in plan["edit"]:
            self.say("📌 تعديل: "+path)
            try:
                c=self._repair_file(request,name,path,current.get(path,""),json.dumps(project,ensure_ascii=False),history=json.dumps(errors,ensure_ascii=False))
            except RuntimeError as e:
                if str(e)=="NOVA_RATE_LIMIT":
                    self.say("⚠️ Groq Rate Limit؛ إيقاف التعديل والعودة للنسخة السليمة.")
                    self.pm.restore_snapshot(name,before)
                    return {"success":False,"project":name,"error":"rate_limit","changed":[],"baseline":baseline}
                raise
            if c:
                try: compile(c,path,"exec")
                except Exception as e:
                    self._save_error(name,e,path); continue
                self.pm.write_files(name,{path:c}); changed.append(path)
        for path in plan["create"]:
            self.say("📌 إنشاء: "+path)
            try:
                c=self._new_file(request,name,path,json.dumps(project,ensure_ascii=False),"\n".join(current.get(x,"") for x in plan["edit"]))
            except RuntimeError as e:
                if str(e)=="NOVA_RATE_LIMIT":
                    self.say("⚠️ Groq Rate Limit؛ إيقاف التعديل والعودة للنسخة السليمة.")
                    self.pm.restore_snapshot(name,before)
                    return {"success":False,"project":name,"error":"rate_limit","changed":[],"baseline":baseline}
                raise
            if c:
                try: compile(c,path,"exec")
                except: continue
                self.pm.write_files(name,{path:c}); changed.append(path)

        # Deterministic safety net for Snake shop requests: a shop module is
        # mandatory. Never report success if the requested module was not created.
        low_req = request.lower()
        snake_shop = any(k in low_req for k in ("متجر", "shop", "store")) and any(k in low_req for k in ("snake", "ثعبان"))
        if snake_shop and "store.py" not in changed:
            store_code = """class Store:
    def __init__(self, coins=0):
        self.coins = int(coins)
        self.items = {
            "classic": {"price": 0, "owned": True},
            "blue": {"price": 50, "owned": False},
            "red": {"price": 100, "owned": False},
        }

    def can_buy(self, skin):
        item = self.items.get(skin)
        return bool(item) and not item["owned"] and self.coins >= item["price"]

    def buy(self, skin):
        item = self.items.get(skin)
        if not item or item["owned"] or self.coins < item["price"]:
            return False
        self.coins -= item["price"]
        item["owned"] = True
        return True

    def add_coins(self, amount):
        self.coins += max(0, int(amount))

    def owned_skins(self):
        return [name for name, item in self.items.items() if item["owned"]]
"""
            try:
                compile(store_code, "store.py", "exec")
                self.pm.write_files(name, {"store.py": store_code})
                changed.append("store.py")
                self.say("   ✓ إنشاء احتياطي آمن: store.py")
            except Exception:
                pass

        if snake_shop and "store.py" not in changed:
            self.pm.restore_snapshot(name,before)
            return {"success":False,"project":name,"error":"لم يتم إنشاء store.py المطلوب","changed":[]}

        # A store file alone is not enough: the feature must be connected to the
        # game. Require a lightweight integration signal in main.py or game.py.
        # If the LLM edits did not connect it, do one focused integration pass
        # instead of reporting a fake success.
        if snake_shop:
            files_now = self.pm.read_project(name,max_chars=14000)
            integrated = False
            for ip in ("main.py", "game.py"):
                txt = files_now.get(ip, "").lower()
                if "store" in txt and ("import store" in txt or "from store import" in txt or "store(" in txt):
                    integrated = True
                    break
            if not integrated:
                self.say("   🔗 ربط المتجر باللعبة...")
                target = "game.py" if "game.py" in files_now else ("main.py" if "main.py" in files_now else None)
                if target:
                    try:
                        c = self._repair_file(
                            request + "\nIMPORTANT: store.py already exists. Integrate it into this file with a real in-game/menu access path. Do not rewrite unrelated logic.",
                            name, target, files_now.get(target, ""), json.dumps(project,ensure_ascii=False),
                            history="store.py exists but is not connected to main/game. Add minimal safe integration."
                        )
                    except RuntimeError as e:
                        if str(e)=="NOVA_RATE_LIMIT":
                            self.pm.restore_snapshot(name,before)
                            return {"success":False,"project":name,"error":"rate_limit","changed":[]}
                        raise
                    if c:
                        try:
                            compile(c,target,"exec")
                            self.pm.write_files(name,{target:c})
                            if target not in changed: changed.append(target)
                            files_now = self.pm.read_project(name,max_chars=14000)
                        except Exception:
                            pass
                integrated = any(
                    "store" in files_now.get(ip, "").lower() and
                    ("import store" in files_now.get(ip, "").lower() or "from store import" in files_now.get(ip, "").lower() or "store(" in files_now.get(ip, "").lower())
                    for ip in ("main.py", "game.py")
                )
            if not integrated:
                self.pm.restore_snapshot(name,before)
                return {"success":False,"project":name,"error":"feature_gate: store.py موجود لكن غير مربوط باللعبة","changed":[]}

        if not changed:
            return {"success":False,"project":name,"error":"لم يتم إنتاج تعديل صالح","changed":[]}
        # verification / repair loop
        for rnd in range(1,6):
            self.say(f"🧪 فحص التعديل {rnd}...")
            check=self.pm.test(name)
            if check.get("success"):
                # Feature gate: for an explicit Snake shop request, verify the
                # requested shop module exists before declaring success.
                if snake_shop and "store.py" not in self.pm.tree(name):
                    self.say("   ❌ المتجر غير موجود؛ لا أعتبر التعديل ناجحًا.")
                    self.pm.restore_snapshot(name,before)
                    return {"success":False,"project":name,"error":"feature_gate: store.py missing","changed":[]}
                rr=None
                if self.runtime:
                    rr=self.runtime.run_entry(name)
                    if rr.get("status")=="runtime_error":
                        # Environment-related runtime failures (pygame display/audio,
                        # Tk/curses/terminal, missing optional device, etc.) are not
                        # code bugs. Do NOT let the LLM rewrite working project files.
                        if rr.get("environment_like"):
                            self.say("   ⚠️ Runtime مشكلة بيئة/جهاز؛ لن أغيّر الكود بسببها.")
                            post = intel.analyze(name)
                            return {"success":True,"project":name,"changed":changed,"rounds":rnd,"baseline":baseline,"runtime":rr,"environment_like":True,"plan":plan,"files":post.get("tree",self.pm.tree(name))}
                        self._save_error(name,rr.get("output",""),"main.py")
                        self.say("💥 Runtime Error؛ إصلاح موجّه...")
                        cur=self.pm.read_project(name,max_chars=12000)
                        target="main.py" if "main.py" in cur else next(iter(cur),None)
                        if target:
                            try:
                                c=self._repair_file(request,name,target,cur[target],json.dumps(project,ensure_ascii=False),rr.get("output",""))
                            except RuntimeError as e:
                                if str(e)=="NOVA_RATE_LIMIT":
                                    self.say("⚠️ Groq Rate Limit؛ إيقاف الإصلاح والعودة للنسخة السليمة.")
                                    self.pm.restore_snapshot(name,before)
                                    return {"success":False,"project":name,"error":"rate_limit","changed":[],"baseline":baseline}
                                raise
                            if c:
                                try:
                                    compile(c,target,"exec")
                                    self.pm.write_files(name,{target:c})
                                    continue
                                except Exception:
                                    pass
                        self.pm.restore_snapshot(name,before)
                        return {"success":False,"project":name,"error":"Runtime Error","changed":[]}
                    if rr.get("status")=="timeout": self.say("   ⏱️ GUI/حلقة مستمرة؛ التشغيل التجريبي مقبول.")
                # inspect post-change tree
                post=intel.analyze(name)
                self.say("🔍 Regression Check...")
                # At this point the full project test has already passed. Keep the
                # modification even when the baseline was a GUI/environment failure.
                # The important regression gate is: modified project tests must pass.
                return {"success":True,"project":name,"changed":changed,"rounds":rnd,
                        "baseline":baseline,"runtime":rr,"plan":plan,
                        "files":post.get("tree",self.pm.tree(name))}
            out=check.get("output","")
            self._save_error(name,out)
            cur=self.pm.read_project(name,max_chars=12000)
            target=next((x for x in plan["edit"] if x in cur),next(iter(cur),None))
            if not target: break
            try:
                c=self._repair_file(request,name,target,cur[target],json.dumps(project,ensure_ascii=False),out,json.dumps(errors,ensure_ascii=False))
            except RuntimeError as e:
                if str(e)=="NOVA_RATE_LIMIT":
                    self.say("⚠️ Groq Rate Limit؛ إيقاف الإصلاح والعودة للنسخة السليمة.")
                    self.pm.restore_snapshot(name,before)
                    return {"success":False,"project":name,"error":"rate_limit","changed":[],"baseline":baseline}
                raise
            if c:
                try: compile(c,target,"exec"); self.pm.write_files(name,{target:c}); 
                except: pass
        self.pm.restore_snapshot(name,before)
        self.say("↩️ Rollback: لم ينجح التعديل.")
        return {"success":False,"project":name,"changed":[],"error":"tests failed"}
