import os, json
class ProjectDashboard:
    def __init__(self,pm,brain,deps,versions): self.pm=pm; self.brain=brain; self.deps=deps; self.versions=versions
    def text(self,name):
        info=self.brain.scan(name); deps=self.deps.scan(name); versions=self.versions.list(name)
        lines=['╔════════════════ NOVA PROJECT DASHBOARD ════════════════╗',f'  Project: {name}',f"  Type: {info.get('project_type')}",f"  Files: {len(info.get('files',[]))}",f"  Python: {len(info.get('python_files',[]))}",f"  Functions: {info.get('functions',0)} | Classes: {info.get('classes',0)}",'  Files:']
        lines += ['    • '+x for x in info.get('files',[])[:30]]
        lines += ['  Dependencies: '+(', '.join(deps) if deps else 'none'),f'  Versions: {len(versions)}','╚════════════════════════════════════════════════════════╝']
        return '\n'.join(lines)
