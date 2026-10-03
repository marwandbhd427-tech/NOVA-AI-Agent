import os,re,hashlib
TEXT_EXT={'.py','.txt','.md','.json','.csv','.xml','.html','.css','.js','.ts','.java','.c','.cpp','.h','.hpp','.yaml','.yml','.ini','.cfg','.log'}
def analyze_file(path):
    path=os.path.abspath(path)
    if not os.path.isfile(path):return {'success':False,'error':'الملف غير موجود.'}
    b=open(path,'rb').read();o={'success':True,'path':path,'name':os.path.basename(path),'extension':os.path.splitext(path)[1].lower(),'size_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    try:
        text=b.decode('utf-8');o.update({'type':'text','lines':len(text.splitlines()),'characters':len(text),'words':len(re.findall(r'\S+',text))})
        if o['extension']=='.py':o.update({'classes':len(re.findall(r'^\s*class\s+',text,re.M)),'functions':len(re.findall(r'^\s*def\s+',text,re.M)),'imports':len(re.findall(r'^\s*(?:from|import)\s+',text,re.M))})
    except Exception:o['type']='binary'
    return o
def read_file(path,max_chars=50000):
    path=os.path.abspath(path)
    if not os.path.isfile(path):return {'success':False,'error':'الملف غير موجود.'}
    try:
        s=open(path,encoding='utf-8').read(max_chars+1);return {'success':True,'path':path,'content':s[:max_chars],'truncated':len(s)>max_chars}
    except Exception as e:return {'success':False,'error':str(e)}
def analyze_folder(path):
    path=os.path.abspath(path)
    if not os.path.isdir(path):return {'success':False,'error':'المجلد غير موجود.'}
    files=[];size=0
    for base,dirs,names in os.walk(path):
        dirs[:]=[d for d in dirs if d not in {'.git','__pycache__','.venv','venv'}]
        for n in names:
            p=os.path.join(base,n);files.append(os.path.relpath(p,path));size+=os.path.getsize(p)
    return {'success':True,'path':path,'files':files,'file_count':len(files),'size_bytes':size}
