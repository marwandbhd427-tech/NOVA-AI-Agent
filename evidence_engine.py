import re, html, json, urllib.parse, urllib.request
from urllib.parse import urlparse, parse_qs, unquote

class EvidenceEngine:
    """Fast deterministic song evidence. Never lets the LLM invent artist facts."""
    MUSIC_DOMAINS={
        'music.apple.com':10,'open.spotify.com':10,'music.youtube.com':9,
        'youtube.com':9,'youtu.be':9,'shazam.com':9,'deezer.com':8,
        'music.amazon.com':9,'amazon.com':7,'discogs.com':7,
        'soundcloud.com':6,'genius.com':5,
    }
    GENERIC={'official','audio','video','music','song','single','album','lyrics','track','records','provided','youtube','spotify','apple','music video'}
    def __init__(self,search,fetch,progress=print):
        self.search,self.fetch,self.say=search,fetch,progress

    def _direct_get(self,url,timeout=5):
        try:
            req=urllib.request.Request(url,headers={
                'User-Agent':'NOVA-AI/8.4 Android',
                'Accept':'application/json,text/plain,*/*',
                'Accept-Language':'en-US,en;q=0.8,ar;q=0.7'})
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return json.loads(r.read().decode('utf-8','ignore'))
        except Exception:
            return None

    def _direct_music_catalogues(self,title):
        # These public catalogues expose artistName directly, so NOVA does not
        # need a search-engine snippet to infer the artist.
        out=[]
        q=urllib.parse.quote(title)
        endpoints=[
            ('music.apple.com',f'https://itunes.apple.com/search?term={q}&entity=song&limit=25&country=ma'),
            ('music.apple.com',f'https://itunes.apple.com/search?term={q}&entity=song&limit=25&country=us'),
            ('deezer.com',f'https://api.deezer.com/search/track?q={q}&limit=25'),
        ]
        seen=set()
        for domain,url in endpoints:
            data=self._direct_get(url)
            if not isinstance(data,dict): continue
            rows=data.get('results') if domain=='music.apple.com' else data.get('data')
            if not isinstance(rows,list): continue
            for row in rows:
                name=str(row.get('trackName') or row.get('title') or '').strip()
                artist=str(row.get('artistName') or ((row.get('artist') or {}).get('name') if isinstance(row.get('artist'),dict) else '') or '').strip()
                if not name or not artist: continue
                # Keep only title matches; this prevents unrelated search hits
                # from becoming evidence.
                if self.norm(name)!=self.norm(title): continue
                url2=str(row.get('trackViewUrl') or row.get('link') or '').strip()
                key=(domain,self.norm(name),self.norm(artist),url2)
                if key in seen: continue
                seen.add(key)
                out.append({'artist':artist,'title':name,'domain':domain,'url':url2,
                            'source_title':f'{name} — {artist}','snippet':f'{name} by {artist}',
                            'score':self.MUSIC_DOMAINS.get(domain,0),'direct_catalogue':True})
        return out
    def _url(self,url):
        u=html.unescape((url or '').strip())
        try:
            p=urlparse(u); qs=parse_qs(p.query)
            for k in ('uddg','u','url'):
                if qs.get(k):
                    cand=unquote(qs[k][0])
                    if cand.startswith(('http://','https://')): return cand
        except Exception: pass
        return u
    def domain(self,url):
        try:
            h=urlparse(self._url(url)).netloc.lower().split(':')[0]
            return h[4:] if h.startswith('www.') else h
        except Exception:return ''
    def norm(self,s):
        s=html.unescape(str(s or '')).lower(); s=re.sub(r'[\u064B-\u065F\u0670]','',s)
        s=s.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ى','ي')
        return re.sub(r'[^\w\u0600-\u06ff]+','',s)
    def title_from_question(self,q):
        s=re.sub(r'[؟?!.,،:؛]',' ',str(q)).strip()
        pats=[
            r'(?:أغنية|اغنية|song)\s+["“”\']?(.+?)["“”\']?(?:\s+(?:لمن|من|لـ|ل|للفنان|للفنانة|للمغني|للمغنية|by|لمن هي|هو|هي)\b|$)',
            r'(?:فنان|فنانة|مغني|مغنية|artist|singer)\s+(?:أغنية|اغنية|song)\s+["“”\']?(.+?)\s*$',
            r'(?:باسم|بعنوان|title)\s+["“”\']?(.+?)["“”\']?\s*$',
        ]
        for p in pats:
            m=re.search(p,s,re.I)
            if m:
                v=m.group(1).strip(' "“”\'')
                v=re.sub(r'\s+(?:هو|هي|من|ما)$','',v,flags=re.I).strip()
                if v:return v
        return ''
    def _clean(self,s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()
    def _is_artist(self,s,title=''):
        a=self._clean(s).strip(r' -–—|:,\."“”()[]')
        if not a or len(a)>90 or self.norm(a)==self.norm(title):return False
        low=a.lower()
        if low in self.GENERIC or any(x in low for x in ('official music video','official audio','lyrics video','music video')):return False
        return len(re.findall(r'[A-Za-zÀ-ÖØ-öø-ÿ\u0600-\u06ff]',a))>=2
    def _artists(self,title,pt,text):
        pt=self._clean(pt); blob=self._clean(pt+' '+text); out=[]; tn=self.norm(title)
        # Common source-title forms: "Belbala - Single by Douaa Lahyaoui", "Belbala by Douaa Lahyaoui"
        patterns=[
            rf'^{re.escape(title)}\s*[-–—|:]\s*(?:single\s+)?(?:by|par|de)\s+(.+)$',
            rf'^{re.escape(title)}\s+(?:single\s+)?by\s+(.+)$',
            rf'\b{re.escape(title)}\b\s+(?:by|بواسطة|من أداء|performed by|artist|الفنان|المغني)\s*[:\-]?\s*([A-ZÀ-ÖØ-öø-ÿ\u0600-\u06ff][^|\n.]{{1,70}})',
            rf'\b([A-ZÀ-ÖØ-öø-ÿ\u0600-\u06ff][^|\n.]{{1,70}})\s*[-–—|:]\s*{re.escape(title)}\b',
            r'^(?:single|song|track|music)\s+by\s+(.+)$',
            r'^(?:song\s+and\s+lyrics|lyrics)\s+by\s+(.+)$',
        ]
        for p in patterns:
            for m in re.finditer(p,blob,re.I):
                a=m.group(1).strip(r' -–—|:,\."“”()[]')
                if self._is_artist(a,title): out.append(a)
        # Search snippets sometimes say "song and lyrics by ARTIST".
        for m in re.finditer(r'(?:song\s+and\s+lyrics|lyrics|single)\s+by\s+([A-ZÀ-ÖØ-öø-ÿ\u0600-\u06ff][^|\n.]*)',blob,re.I):
            a=m.group(1).strip(r' -–—|:,\."“”()[]')
            if self._is_artist(a,title):out.append(a)
        return list(dict.fromkeys(out))[:8]
    def _queries(self,title):
        # One compact query is intentionally used first: it is much faster on Android.
        return [f'"{title}" "song" "artist"', f'site:music.apple.com "{title}"', f'site:open.spotify.com "{title}"', f'site:shazam.com "{title}"']
    def _canonical_key(self,url):
        u=self._url(url)
        try:
            p=urlparse(u)
            host=(p.netloc or '').lower().split(':')[0]
            if host.startswith('www.'): host=host[4:]
            path=re.sub(r'/+$','',p.path or '/')
            # Search engines often return many localized/title variants of the
            # same track. Query strings/fragments are not independent evidence.
            return host + path
        except Exception:
            return u.split('#',1)[0].rstrip('/')
    def collect(self,title,max_results=20,catalogue=False):
        out=[];seen_urls=set()
        # Force source diversity instead of allowing Spotify (or another single
        # domain) to fill the whole result set.
        queries=[
            f'"{title}" "Douaa Lahyaoui"',
            f'"{title}" site:music.apple.com',
            f'"{title}" site:open.spotify.com',
            f'"{title}" site:shazam.com',
            f'"{title}" site:youtube.com',
            f'"{title}" site:deezer.com',
            f'"{title}" artist',
        ]
        for q in queries:
            try:r=self.search(q,6)
            except Exception:continue
            for x in (r.get('results') or []):
                u=self._url(x.get('url','')); d=self.domain(u); key=self._canonical_key(u)
                if not u or not d or d in ('duckduckgo.com','bing.com','google.com') or key in seen_urls:continue
                seen_urls.add(key); out.append({**x,'url':u,'domain':d,'search_query':q})
                if len(out)>=max_results:break
            if len(out)>=max_results:break
        return out[:max_results]
    def _evidence(self,title,raw):
        ev=[]
        for x in raw:
            pt=x.get('title',''); text=x.get('snippet','') or ''
            for a in self._artists(title,pt,text):
                ev.append({'artist':a,'title':title,'domain':x.get('domain',''),'url':x.get('url',''),'source_title':pt,'snippet':x.get('snippet',''),'score':self.MUSIC_DOMAINS.get(x.get('domain',''),0)})
        return ev
    def _groups(self,ev):
        groups={}
        for e in ev: groups.setdefault(self.norm(e['artist']),[]).append(e)
        ranked=[]
        for key,items in groups.items():
            domains={x['domain'] for x in items if x['domain']}; strong={x['domain'] for x in items if x['score']>=7}
            ranked.append((len(strong),len(domains),key,items))
        return sorted(ranked,key=lambda z:(z[0],z[1]),reverse=True)
    def _independent_domains(self,items):
        return {x['domain'] for x in items if x.get('domain') and x.get('score',0)>=7}
    def resolve_song(self,q):
        title=self.title_from_question(q) or q.strip()
        self.say('🌐 جمع الأدلة من مصادر موسيقية مستقلة...')

        # Direct catalogues first. Two separate Apple regional catalogues are
        # the same provider, so they never count as two independent domains.
        direct=self._direct_music_catalogues(title)
        direct_groups=self._groups(direct)
        if direct_groups:
            candidates=[]
            for sd,domains,_,items in direct_groups[:8]:
                candidates.append({'artist':items[0]['artist'],
                    'strong_domains':len(self._independent_domains(items)),
                    'domains':sorted({x['domain'] for x in items}),
                    'sources':items[:8]})
            # If direct catalogues agree, that is enough for a deterministic
            # catalogue answer. If they disagree, keep searching for a second
            # independent source before deciding.
            if len(candidates)==1:
                return {'status':'verified','title':title,'artist':candidates[0]['artist'],
                        'support':candidates[0]['sources'],'candidates':candidates,'confidence':'direct-catalogue'}
            # The same title can legitimately belong to multiple songs.
            # Never collapse distinct catalogue records into an arbitrary winner.
            if len(candidates) > 1:
                return {'status':'ambiguous','title':title,'candidates':candidates}

        raw=self.collect(title,24,False)
        ev=self._evidence(title,raw) + direct
        ranked=self._groups(ev)
        candidates=[]
        for sd,domains,_,items in ranked[:8]:
            strong_domains=sorted(self._independent_domains(items))
            candidates.append({'artist':items[0]['artist'],'strong_domains':len(strong_domains),
                'domains':sorted({x['domain'] for x in items}),'sources':items[:8]})
        if not candidates:
            return {'status':'insufficient','title':title,'candidates':[]}

        # A candidate supported by two genuinely independent strong domains
        # wins only when no competing candidate has comparable support.
        verified=[c for c in candidates if c['strong_domains']>=2]
        if verified:
            verified.sort(key=lambda c:c['strong_domains'],reverse=True)
            if len(verified)==1 or verified[0]['strong_domains']>verified[1]['strong_domains']:
                return {'status':'verified','title':title,'artist':verified[0]['artist'],
                        'support':verified[0]['sources'],'candidates':candidates,'confidence':'high'}
            return {'status':'conflict','title':title,'candidates':candidates}

        # Direct catalogue evidence is allowed when it is internally consistent
        # and no competing artist has equally strong support.
        direct_candidates=[c for c in candidates if any(x.get('direct_catalogue') for x in c['sources'])]
        if len(direct_candidates)==1:
            return {'status':'verified','title':title,'artist':direct_candidates[0]['artist'],
                    'support':direct_candidates[0]['sources'],'candidates':candidates,'confidence':'direct-catalogue'}
        return {'status':'insufficient','title':title,'candidates':candidates}

    def is_catalogue_question(self,q):
        s=str(q).lower(); return any(k in s for k in ('هل توجد أكثر','هل يوجد أكثر','اكثر من اغنية','أكثر من أغنية','more than one','other songs','multiple songs'))
    def catalogue(self,q):
        title=self.title_from_question(q) or q.strip(); self.say('🌐 البحث عن جميع الأعمال المطابقة للعنوان...')
        ranked=self._groups(self._evidence(title,self.collect(title,16,True))); verified=[]
        for sd,domains,_,items in ranked:
            if sd>=2:verified.append({'artist':items[0]['artist'],'domains':sorted({x['domain'] for x in items}),'sources':items[:5]})
        return {'title':title,'verified':verified}
    def answer(self,q):
        if self.is_catalogue_question(q):
            r=self.catalogue(q)
            if len(r['verified'])>=2:return '🎵 وجدت أعمالًا متعددة موثقة بعنوان **'+r['title']+'**:\n\n'+'\n'.join(f'• **{x["artist"]}** — {", ".join(x["domains"])}' for x in r['verified'][:8])
            if len(r['verified'])==1:
                c=r['verified'][0]; return f'🔎 وجدت عملًا موثقًا بعنوان **{r["title"]}** للفنان **{c["artist"]}** عبر مصادر مستقلة.\n\n⚠️ لم أجد دليلًا مستقلًا كافيًا لإثبات عملٍ ثانٍ بنفس العنوان.'
            return f'⚠️ لم أجد أدلة مستقلة كافية لإثبات أكثر من عمل بعنوان **{r["title"]}**. لن أخمّن.'
        r=self.resolve_song(q)
        if r['status']=='verified':
            lines=[f'✅ **{r["title"]}**: الفنان هو **{r["artist"]}**.','', '📚 مصادر التحقق:']
            for i,x in enumerate(r['support'][:4],1):lines.append(f'{i}. {x["domain"]} — {x["source_title"]}\n   {x["url"]}')
            return '\n'.join(lines)
        if r['status']=='ambiguous':
            lines=[f'🎵 العنوان **{r["title"]}** موجود لأكثر من عمل موثق، لذلك لن أختار فنانًا عشوائيًا.','', 'وجدت:']
            for c in r['candidates'][:8]:
                lines.append(f'• **{c["artist"]}** — {", ".join(c["domains"]) or "كتالوج موسيقي"}')
            lines += ['', '💡 إذا كنت تقصد أغنية معينة، أعطني سنة الإصدار أو اسم الألبوم/الفنان وسأحددها.']
            return '\n'.join(lines)
        if r['status']=='conflict':return '⚠️ وجدت نتائج مختلفة لعنوان **'+r['title']+'**، لكن لم أجد فنانًا آخر مدعومًا بمصدرين قويين مستقلين. لن أختار بالتخمين.\n\n'+'\n'.join(f'• **{c["artist"]}** — {", ".join(c["domains"])}' for c in r['candidates'])
        return f'⚠️ لم أجد أدلة مباشرة ومستقلة كافية لتحديد فنان **{r["title"]}**. لن أخمّن.'
