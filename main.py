from datetime import datetime
import os,re,sys
from config import get_groq_key
from neural_brain import create_brain
from memory import load_memory,save_memory,add_memory,get_facts,save_conversation,memory_status
from language_engine import LanguageEngine
from code_agent import CodeAgent
from tool_router import ToolRouter
from web_search import search_web, fetch_page
from plugin_manager import load_plugins,plugin_status
from task_manager import add as add_task,complete as complete_task,list_tasks
from scheduler import Scheduler
from file_analyzer import analyze_file,read_file,analyze_folder
from project_manager import ProjectManager
from multi_file_agent import MultiFileAgent
from system_tools import system_info
from autonomous_agent import AutonomousAgent
from runtime_agent import RuntimeAgent
from project_intelligence import ProjectIntelligence
from project_edit_agent import ProjectEditAgent
from project_brain import ProjectBrain
from dependency_manager import DependencyManager
from version_manager import VersionManager
from multi_agent import MultiAgentOrchestrator
from dashboard import ProjectDashboard
from project_memory import ProjectMemory
from offline_queue import OfflineQueue
from workspace_agent import WorkspaceAgent
from qa_agent import QAAgent
from research_agent import ResearchAgent
from verified_web import VerifiedWeb
from evidence_engine import EvidenceEngine
from universal_agent import UniversalAgent
from file_command_agent import FileCommandAgent
from execution_context import ExecutionContext, AuditLog
from capability_registry import CapabilityRegistry
from transaction_engine import TransactionEngine
from project_health import ProjectHealth
from self_healing import SelfHealingEngine
from android_agent import AndroidProjectAgent
from agent_orchestrator_v2 import AgentOrchestratorV2
from project_rules import ProjectRules
from project_templates import ProjectTemplates
VERSION='11.1.0'
api_key=get_groq_key();memory=load_memory();brain=create_brain()
language_engine=LanguageEngine(api_key) if api_key else None
code_agent=CodeAgent(language_engine) if language_engine else None
router=ToolRouter(language_engine,code_agent,memory) if language_engine or code_agent else None
pm=ProjectManager();agent=MultiFileAgent(language_engine,pm)
agent_progress=[]
def agent_log(msg):
    agent_progress.append(str(msg)); print('AGENT:',msg)
auto_agent=AutonomousAgent(language_engine,pm,max_rounds=8,progress=agent_log,code_agent=code_agent)
runtime_agent=RuntimeAgent(pm,progress=agent_log,timeout=8)
project_intel=ProjectIntelligence(pm)
edit_agent=ProjectEditAgent(language_engine,pm,runtime=runtime_agent,progress=agent_log) if language_engine else None
project_brain=ProjectBrain(pm)
dep_manager=DependencyManager(pm)
version_manager=VersionManager(pm)
dashboard=ProjectDashboard(pm,project_brain,dep_manager,version_manager)
orchestrator=MultiAgentOrchestrator(language_engine,auto_agent,edit_agent,project_brain,progress=agent_log)
project_memory=ProjectMemory()
offline_queue=OfflineQueue()
qa_agent=QAAgent(pm,runtime_agent,progress=agent_log)
research_agent=ResearchAgent(search_web,progress=agent_log)
verified_web=VerifiedWeb(search_web,fetch_page,language_engine,progress=agent_log)
evidence_engine=EvidenceEngine(search_web,fetch_page,progress=agent_log)
universal_agent=UniversalAgent(language_engine,progress=agent_log)
file_command_agent=FileCommandAgent()
workspace=WorkspaceAgent(orchestrator,pm,project_brain,project_memory,offline_queue,progress=agent_log)
def ctx():
    facts = get_facts(memory)
    if not isinstance(facts, list):
        return ''
    return '\n'.join(str(f.get('value','')) for f in facts[-12:] if isinstance(f,dict))
def fmt(tool,r):
    if isinstance(r,dict):
        if r.get('success') is False:
            err=r.get('error','تعذر التنفيذ')
            if err=='rate_limit': return '⚠️ Groq وصل لحد الاستخدام مؤقتًا. تم إيقاف التعديل والعودة للنسخة السليمة. جرّب الطلب لاحقًا.'
            return '❌ '+str(err)
        if tool=='weather' and 'current' in r:
            c=r['current'];return f"🌤️ {r.get('location','')}\nالحرارة: {c.get('temperature')}°C\nالحالة: {c.get('condition')}\nالرطوبة: {c.get('humidity')}%\nالرياح: {c.get('wind_speed')} km/h"
        if tool=='currency':return f"💱 {r.get('amount')} {r.get('from')} = {r.get('converted',r.get('result'))} {r.get('to')}"
        if tool=='project_run':
            st=r.get('status'); deps=r.get('dependencies',[])
            if st=='ok': msg='▶️ التشغيل التجريبي نجح.'
            elif st=='timeout': msg='⏱️ انتهى وقت الاختبار؛ يبدو أن البرنامج يعمل بحلقة/GUI مستمرة، لذلك لم يُعتبر فشلًا.'
            elif st=='missing': msg='❌ ملف التشغيل غير موجود.'
            else: msg='💥 Runtime Error:\n'+str(r.get('output',''))
            if deps: msg+='\n📦 مكتبات خارجية: '+', '.join(deps)
            return msg
        if tool=='project_deps': return '📦 لا توجد مكتبات خارجية.' if not r else '📦 '+', '.join(r)
        if tool=='health':
            if isinstance(r,dict) and r.get('score') is not None:
                return (f"🏥 {r.get('project')}\n📊 {r.get('score')}/100 ({r.get('grade')})\n"
                        f"📁 {r.get('files')} files | 🧪 {'PASS' if r.get('tests_ok') else 'FAIL'}\n"
                        f"🐞 Syntax: {r.get('syntax_errors')} | 📦 Deps: {len(r.get('external_dependencies',[]))}")
            return str(r)
        if tool=='android':
            return ('📱 Android/Pydroid\n'+str(r.get('project'))+'\n'+
                    'APK config: '+('YES' if r.get('apk_ready') else 'NO')+'\n'+
                    'Dependencies: '+(', '.join(r.get('dependencies',[])) or 'none')+'\n'+
                    'Notes: '+' | '.join(r.get('pydroid_notes',[]))) if isinstance(r,dict) else str(r)
        if tool=='capabilities':
            return '\n'.join(f"• {x['name']} — {x['description']}" for x in r)
        if tool=='templates':
            return '\n'.join(f"• {k}: {', '.join(v)}" for k,v in r.items())
        if tool=='rules':
            return '📐 لا توجد قواعد.' if not r else '\n'.join(f"{i+1}. {x}" for i,x in enumerate(r))
        if tool=='agent':
            files = []
            if r.get('project'):
                try: files = pm.tree(r.get('project'))
                except: files = []
            if not files: files = r.get('files') or r.get('changed') or []
            return ('🎉 نجح المشروع' if r.get('success') else '⚠️ انتهى الإصلاح قبل النجاح') + f"\n📁 {r.get('project')}\n🔁 جولات: {r.get('rounds')}\n📦 الملفات: {len(files)}"

        if 'result' in r:return str(r['result'])
    return str(r)
def local(t):
    l=t.strip().lower()
    if l in {'exit','quit','خروج','اغلاق','إغلاق'}:return '__EXIT__'
    if l in {'كم الساعة','كم الساعه','الساعة كم','الساعه كم','الوقت','شو الوقت','شو الساعة'}:return datetime.now().strftime('الوقت الآن: %H:%M:%S')
    if l in {'system status','حالة النظام','حاله النظام'}:return str(system_info())
    if l in {'memory status','حالة الذاكرة','حاله الذاكره'}:return str(memory_status(memory))
    if l in {'plugins','plugin status','حالة plugins'}:return str(plugin_status())
    if l in {'tasks','المهام','قائمة المهام'}:return '\n'.join(f"{x['id']} | [{'x' if x['done'] else ' '}] {x['title']}" for x in list_tasks(True)) or 'لا توجد مهام.'
    if l in {'projects','المشاريع'}:return '\n'.join(pm.list_projects()) or 'لا توجد مشاريع.'
    if l in {'المشروع الحالي','المشروع الحالي؟','active project','current project'}:
        return '📁 المشروع الحالي: '+str(active_project_name() or 'لا يوجد مشروع نشط.')
    if l in {'nova status','حالة نوفا','حاله نوفا','nova health'}:
        cs=capabilities.summary()
        return ('🧠 NOVA V11.0\n'
                f'Capabilities: {cs["enabled"]}/{cs["count"]} enabled\n'
                f'Active project: {active_project_name() or "none"}\n'
                f'Projects: {len(pm.list_projects())}\n'
                'Orchestrator: ON | Transactions: ON | Self-Healing: ON | Health: ON | Android Intelligence: ON')
    if l in {'capabilities','القدرات','قدرات نوفا'}:
        return '\n'.join(f"• {x['name']}: {x['description']} [{x['risk']}]" for x in capabilities.list())
    if l in {'ماذا تستطيع','ماذا يمكنك','مساعده','مساعدة','help','nova help'}:
        return ('🤖 NOVA V11\n'
                '• اسأل أي سؤال طبيعي\n'
                '• ابحث وتحقق من المعلومات\n'
                '• أنشئ مشاريع/ألعاب/تطبيقات\n'
                '• عدّل المشروع الحالي\n'
                '• شغّل واختبر وأصلح المشاريع\n'
                '• اقرأ وحلل الملفات\n'
                '• أنشئ ملفات ومجلدات\n'
                '• snapshots وrollback وذاكرة المشروع\n'
                'مثال: اعمل لي لعبة Snake ببايثون')
    if l in {'agent help','مساعدة الوكيل'}:
        return '🤖 أمثلة: agent اعمل لعبة Snake ببايثون | project run snake_game | project deps snake_game'
    return None
scheduler=None
def callback_reminder(text):print('\n⏰ NOVA REMINDER:',text,'\nYou: ',end='')
scheduler=Scheduler(callback_reminder);scheduler.start()
def latest_project():
    projects=pm.list_projects()
    if not projects:return None
    try:
        return max(projects,key=lambda n: os.path.getmtime(os.path.join(pm.base,n)))
    except: return projects[-1]

def is_project_modification(t):
    l=t.strip().lower()
    keys=('أضف','اضف','ضيف','ضف','عدّل','عدل','تعديل','طوّر','طور','غيّر','غير','اصلح','أصلح',
          'add ','modify ','update ','improve ','change ','fix ','upgrade ')
    return any(k in l for k in keys)

def command(t):
    l=t.lower().strip()
    if l.startswith(("تحقق وابحث ","ابحث وتحقق ","تحقق على الإنترنت ","verify web ")):
        q=re.sub(r"^(تحقق وابحث|ابحث وتحقق|تحقق على الإنترنت|verify web)\s*","",t,flags=re.I).strip(); return "verified_web",verified_web.answer(q)
    if l.startswith(('ابحث عن ','بحث ')):return 'search',search_web(re.sub(r'^(ابحث عن|بحث)\s*','',t,flags=re.I))
    if l.startswith(('اقرأ الملف ','read file ')):return 'file',read_file(re.sub(r'^(اقرأ الملف|read file)\s*','',t,flags=re.I))
    if l.startswith(('حلل الملف ','analyze file ')):return 'file',analyze_file(re.sub(r'^(حلل الملف|analyze file)\s*','',t,flags=re.I))
    if l.startswith(('حلل المجلد ','analyze folder ')):return 'file',analyze_folder(re.sub(r'^(حلل المجلد|analyze folder)\s*','',t,flags=re.I))
    if l.startswith(('أضف مهمة ','task add ')):return 'task',add_task(re.sub(r'^(أضف مهمة|task add)\s*','',t,flags=re.I))
    if l.startswith('task done '):return 'task',complete_task(t.split(None,2)[2])
    m=re.match(r'remind me in\s+(\d+)\s*(seconds?|minutes?|hours?)\s+(.+)',t,re.I)
    if m:
        mult={'second':1,'seconds':1,'minute':60,'minutes':60,'hour':3600,'hours':3600}[m.group(2).lower()];return 'schedule',scheduler.add_after_seconds(int(m.group(1))*mult,m.group(3))
    if l.startswith('project continue'):
        parts=t.split(None,2); req=parts[2].strip() if len(parts)>2 else ''
        return 'agent',workspace.continue_project(req) if req else 'استخدم: project continue الطلب'
    if l.startswith('project memory '):
        name=t.split(None,2)[2].strip(); return 'project',project_memory.summary(name)
    if l.startswith('project qa '):
        name=t.split(None,2)[2].strip(); return 'project',qa_agent.check(name)
    if l in ('agent queue','قائمة الانتظار','agent pending'):
        return 'project',offline_queue.list()
    if l.startswith('agent queue add '):
        return 'project',offline_queue.add('modify',latest_project() or 'pending_project',t.split(None,3)[3].strip())
    if l.startswith('project research '):
        return 'research',research_agent.research(t.split(None,2)[2].strip())
    if l in ('project templates','templates','قوالب المشاريع'):
        return 'templates',project_templates.list()
    if l.startswith('project rules add '):
        parts=t.split(None,3); name=parts[2].strip() if len(parts)>2 else active_project_name(); rule=parts[3].strip() if len(parts)>3 else ''
        if not name:return 'project','⚠️ لا يوجد مشروع نشط.'
        return 'rules',project_rules.add(name,rule)
    if l.startswith('project rules ') or l.startswith('قواعد المشروع'):
        parts=t.split(None,2); name=parts[2].strip() if len(parts)>2 and parts[2].strip() else active_project_name()
        if not name:return 'project','⚠️ لا يوجد مشروع نشط.'
        return 'rules',project_rules.list(name)
    if l.startswith('project health ') or l.startswith('project status '):
        name=t.split(None,2)[2].strip(); return 'health',project_health.analyze(name)
    if l.startswith('project heal ') or l.startswith('self heal '):
        parts=t.split(None,2); name=parts[2].strip() if len(parts)>2 else active_project_name()
        if not name:return 'project','⚠️ لا يوجد مشروع نشط.'
        return 'health',self_healing.heal(name)
    if l.startswith('project android ') or l.startswith('android check '):
        parts=t.split(None,2); name=parts[2].strip() if len(parts)>2 else active_project_name()
        if not name:return 'project','⚠️ لا يوجد مشروع نشط.'
        return 'android',android_agent.analyze(name)
    if l in ('nova capabilities','capabilities','قدرات نوفا'):
        return 'capabilities',capabilities.list()
    if l.startswith('project info '):
        name=t.split(None,2)[2].strip(); return 'project',project_intel.analyze(name)
    if l.startswith('project snapshot '):
        name=t.split(None,2)[2].strip(); return 'project',pm.snapshot(name,'manual')
    if l.startswith('project rollback '):
        name=t.split(None,2)[2].strip()
        snaps=[os.path.join(pm.base,'.snapshots',x) for x in os.listdir(os.path.join(pm.base,'.snapshots')) if x.startswith(name+'__')]
        snap=max(snaps,key=os.path.getmtime) if snaps else None
        return 'project',pm.restore_snapshot(name,snap) if snap else False
    if l.startswith('project modify '):
        parts=t.split(None,3)
        if len(parts)<4:return 'project','استخدم: project modify اسم_المشروع الطلب'
        if not edit_agent:return 'project','⚠️ Language Engine غير متوفر.'
        return 'agent',edit_agent.modify(parts[3],parts[2])
    if l.startswith('project create '):
        name=t.split(None,2)[2].strip(); result=pm.create(name); execution_context.set_project(name); record_action('project_create',t,result); return 'project',result
    if l.startswith('project test '):return 'project',pm.test(t.split(None,2)[2])
    if l.startswith('project tree '):return 'project',pm.tree(t.split(None,2)[2])
    if l.startswith('project dashboard '):
        return 'dashboard',dashboard.text(t.split(None,2)[2].strip())
    if l.startswith(('project brain ','project map ')):
        name=t.split(None,2)[2].strip(); return 'project',project_brain.report(name)
    if l.startswith(('project versions ','project history ')):
        name=t.split(None,2)[2].strip(); return 'project',version_manager.list(name)
    if l.startswith('project checkpoint '):
        parts=t.split(None,2); return 'project',version_manager.create(parts[2].strip(),'manual')
    if l.startswith('project deps write '):
        return 'project_deps',dep_manager.write(t.split(None,3)[3].strip())
    if l.startswith('project deps '):
        parts=t.split(None,2); name=parts[2].strip() if len(parts)>2 else ''; return 'project_deps',dep_manager.scan(name)
    if l.startswith('project run '):
        parts=t.split(None,2)
        if len(parts)<3:return 'project','استخدم: project run اسم_المشروع'
        name=parts[2].strip(); execution_context.set_project(name); rr=runtime_agent.run_entry(name)
        deps=runtime_agent.requirements(name)
        rr['dependencies']=deps
        return 'project_run',rr
    if l.startswith('project requirements '):
        parts=t.split(None,2)
        if len(parts)<3:return 'project','استخدم: project requirements اسم_المشروع'
        name=parts[2].strip();return 'project_deps',dep_manager.scan(name)
    if l.startswith(('agent ', 'وكيل ')):
        req=re.sub(r'^(agent|وكيل)\s*','',t,flags=re.I).strip()
        if not req:return 'agent','اكتب الطلب بعد agent، مثال: agent اعمل لعبة Snake ببايثون'
        if not language_engine:return 'agent','⚠️ Language Engine غير متوفر.'
        return 'agent',auto_agent.run(req)
    return None
def is_coding_request(t):
    l=t.strip().lower()
    # Explicit agent command is handled by command(); this detector is for
    # natural language requests so the autonomous agent gets priority.
    words=(
        'اعمل لعبة','اصنع لعبة','سوي لعبة','سوّي لعبة','برمج لعبة','طور لعبة',
        'اعمل برنامج','اصنع برنامج','سوي برنامج','برمج برنامج','طور برنامج',
        'اعمل تطبيق','اصنع تطبيق','برمج تطبيق','طور تطبيق',
        'مشروع بايثون','مشروع python','python project','create a game',
        'make a game','build a game','create a python project','build a python project',
        'اعمل لي كود','اكتب لي كود','برمج لي','أنشئ مشروع','انشئ مشروع'
    )
    return any(w in l for w in words)

def ask_nova(t):
    x=local(t)
    if x=='__EXIT__':return x
    if x:return x
    for p in ('تعلم:','تعلم ','احفظ:','احفظ ','تذكر:','تذكر '):
        if t.startswith(p):
            v=t[len(p):].strip();add_memory(memory,'fact_'+str(len(get_facts(memory))+1),v);save_memory(memory);return '🧠 تم حفظ المعلومة.'
    # Deterministic tools get first refusal. In particular, weather must never
    # be routed through the generic LLM research layer.
    if router:
        try:
            detected = router.detect_tool(t)
            if detected == 'weather':
                rr = router.route(t)
                return fmt('weather', rr.get('result') if isinstance(rr,dict) else rr)
        except Exception as e:
            print('Router weather warning:', e)

    # Universal Agent: natural-language actions can reach the real execution
    # layer without requiring internal command syntax. Explicit deterministic
    # commands above still have priority.
    try:
        ua = universal_agent.choose(t)
        ui = ua.get('intent') if isinstance(ua, dict) else 'answer'
        if ui == 'create_project' and language_engine:
            agent_log('🧭 Universal Agent: تحويل الطلب إلى Project Agent...')
            try:
                result = orchestrator_v2.create(t)
                if isinstance(result, dict) and result.get('project'): execution_context.set_project(result['project'])
                record_action('create_project', t, result)
                return fmt('agent', result)
            except Exception as e:
                # Never fall through to a generic answer after an execution failure.
                return '❌ فشل تنفيذ طلب إنشاء المشروع: ' + str(e)
        if ui == 'filesystem':
            m = re.search(r'(?:انشئ|انشاء|اعمل|اصنع)\s+(?:ملف|file)\s+([^\s]+)(?:\s+(?:محتواه|بمحتوى|content)\s*[:：]\s*(.*))?$', t, re.I)
            if m:
                return fmt('file', file_command_agent.create_file(m.group(1), m.group(2) or ''))
            m = re.search(r'(?:انشئ|انشاء|اعمل|اصنع)\s+(?:مجلد|folder)\s+([^\s]+)$', t, re.I)
            if m:
                return fmt('file', file_command_agent.create_folder(m.group(1)))
            agent_log('🧭 Universal Agent: طلب ملفات غير مكتمل؛ سأتعامل معه كسؤال بدل التخمين.')
        if ui == 'modify_project' and language_engine and edit_agent:
            name = active_project_name()
            if name:
                agent_log('🧭 Universal Agent: تحديد المشروع الحالي...')
                result = orchestrator_v2.modify(name, t)
                execution_context.set_project(name); record_action('modify_project', t, result)
                return fmt('agent', result)
        if ui in ('project_run','project_test','project_tree'):
            name = active_project_name()
            if name:
                if ui == 'project_run':
                    rr = runtime_agent.run_entry(name); rr['dependencies'] = runtime_agent.requirements(name)
                    record_action('project_run', t, rr); return fmt('project_run', rr)
                if ui == 'project_test':
                    result=pm.test(name); record_action('project_test',t,result); return fmt('project', result)
                return fmt('project', pm.tree(name))
        if ui in ('project_health','project_heal','project_android','nova_status'):
            if ui=='nova_status':
                return local('nova status')
            name=active_project_name()
            if not name:return '⚠️ لا يوجد مشروع نشط.'
            if ui=='project_health':
                result=project_health.analyze(name); record_action('project_health',t,result); return fmt('health',result)
            if ui=='project_heal':
                result=self_healing.heal(name); record_action('project_heal',t,result); return fmt('health',result)
            result=android_agent.analyze(name); record_action('project_android',t,result); return fmt('android',result)
        if ui in ('project_snapshot','project_rollback','project_info','project_deps'):
            name=active_project_name()
            if not name:
                return '⚠️ لا يوجد مشروع نشط.'
            if ui=='project_snapshot':
                result=pm.snapshot(name,'natural'); record_action('project_snapshot',t,result); return '📸 تم إنشاء Snapshot للمشروع: '+name
            if ui=='project_rollback':
                snap_dir=os.path.join(pm.base,'.snapshots')
                snaps=[os.path.join(snap_dir,x) for x in os.listdir(snap_dir)] if os.path.isdir(snap_dir) else []
                snaps=[x for x in snaps if os.path.basename(x).startswith(name+'__')]
                snap=max(snaps,key=os.path.getmtime) if snaps else None
                if not snap:return '⚠️ لا توجد نسخة احتياطية للمشروع.'
                result=pm.restore_snapshot(name,snap); record_action('project_rollback',t,result); return '↩️ تمت استعادة آخر Snapshot.' if result else '❌ فشل الاستعادة.'
            if ui=='project_info':
                result=project_intel.analyze(name); record_action('project_info',t,result); return fmt('project',result)
            result=dep_manager.scan(name); record_action('project_deps',t,result); return fmt('project_deps',result)
        if ui == 'search':
            q = re.sub(r'^(ابحث عن|ابحث لي|دور على|فتش عن|search for|look up)\s*', '', t, flags=re.I).strip()
            rr = search_web(q or t)
            if rr.get('success'):
                return '\n'.join(f"{i+1}. {a['title']}\n{a['url']}" for i,a in enumerate(rr['results']))
        if ui == 'file':
            # Existing explicit file commands are handled below; for vague file
            # requests, ask the language layer instead of guessing a path.
            pass
    except Exception as e:
        print('Universal Agent warning:', e)

    if verified_web.is_fact_query(t) and not is_coding_request(t) and not is_project_modification(t):
        # Song identity questions use a deterministic evidence gate. The LLM
        # is never asked to choose an artist from memory.
        if evidence_engine.title_from_question(t) or any(k in t.lower() for k in ('belbala','bali maak','اغنية','أغنية','song')):
            return evidence_engine.answer(t)
        return 'verified_web',verified_web.answer_grounded(t)

    # A normal question must never fall through to ToolRouter's Code Agent.
    # V9.0 regression: "ما الفرق بين list و tuple؟" was executed as code.
    if ui == 'answer' and language_engine:
        a = language_engine.ask(t, ctx())
        save_conversation(memory, t, a); save_memory(memory)
        return a

    # Natural-language project modifications target the latest existing project.
    if language_engine and is_project_modification(t):
        name=active_project_name()
        if name and edit_agent:
            try:
                return fmt('agent',orchestrator_v2.modify(name,t))
            except Exception as e:
                return '❌ Project Edit Agent error: '+str(e)
    # Autonomous coding must run BEFORE ToolRouter's legacy Code Agent.
    # Otherwise natural requests like 'اعمل لعبة Snake' get intercepted
    # by CodeAgent and never reach the multi-file autonomous pipeline.
    if language_engine and is_coding_request(t):
        try:
            r=orchestrator_v2.create(t)
            if isinstance(r,dict) and r.get('project'): execution_context.set_project(r['project'])
            record_action('create_project',t,r)
            return fmt('agent',r)
        except Exception as e:
            return '❌ Autonomous Agent error: '+str(e)
    c=command(t)
    if c:
        tool,r=c
        if tool=='search' and r.get('success'):return '\n'.join(f"{i+1}. {a['title']}\n{a['url']}" for i,a in enumerate(r['results']))
        return fmt(tool,r)
    if router:
        try:
            r=router.route(t);tool=r.get('tool') if isinstance(r,dict) else None;res=r.get('result') if isinstance(r,dict) else r
            if tool and tool!='language' and res is not None:return fmt(tool,res)
        except Exception as e:print('Router warning:',e)
    if language_engine:
        a=language_engine.ask(t,ctx());save_conversation(memory,t,a);save_memory(memory);return a
    return '⚠️ Language Engine غير متوفر. تأكد من Groq API Key.'
# NOVA Core 10: persistent active-project context + audit trail
execution_context = ExecutionContext()
audit_log = AuditLog()
capabilities = CapabilityRegistry()
transaction_engine = TransactionEngine(pm, audit_log)
project_health = ProjectHealth(pm, project_brain, runtime_agent, dep_manager)
android_agent = AndroidProjectAgent(pm, dep_manager)
self_healing = SelfHealingEngine(pm, runtime_agent, edit_agent, project_health, progress=agent_log)
orchestrator_v2 = AgentOrchestratorV2(pm, project_brain, project_health, transaction_engine, auto_agent, self_healing, progress=agent_log)
project_rules = ProjectRules()
project_templates = ProjectTemplates()

def active_project_name():
    name = execution_context.project()
    if name and os.path.isdir(os.path.join(pm.base, name)):
        return name
    return latest_project()

def record_action(intent, request, result=None):
    try: execution_context.record(intent, request, result)
    except Exception: pass
    try: audit_log.write(intent, request, result)
    except Exception: pass

load_plugins()

def run_cli():
    print(f'\n========================================\n          NOVA V{VERSION} UNIVERSAL READY\n========================================')
    print('بحث | Plugins | Tasks | Scheduler | Files | Projects | Brain 2.0 | Orchestrator | Transactions | Self-Healing | QA | Health | Android | Research | Queue | Tests | Runtime | Versions | GUI')
    print('GUI: python main.py --gui\n')
    while True:
        try:
            t=input('You: ').strip()
        except (EOFError,KeyboardInterrupt):
            break
        if not t:
            continue
        try:
            a=ask_nova(t)
            if a=='__EXIT__':
                break
            print('NOVA:',a,'\n')
        except Exception as e:
            print('NOVA ERROR:',e)

def run_desktop_gui():
    from gui import run_gui
    return run_gui(ask_nova)

def main():
    if '--gui' in sys.argv:
        return run_desktop_gui()
    return run_cli()

if __name__ == '__main__':
    main()
