import re
from urllib.parse import urlparse

class VerifiedWeb:
    """Evidence-first web research.

    Important rule: the language model is NOT allowed to supply a fact that
    was not supported by retrieved web evidence. Ambiguous titles are reported
    as ambiguous instead of guessed.
    """
    TRUSTED_DOMAINS = {
        'music.apple.com': 6, 'open.spotify.com': 6, 'shazam.com': 6,
        'youtube.com': 6, 'youtu.be': 6, 'music.youtube.com': 6,
        'deezer.com': 5, 'discogs.com': 5, 'soundcloud.com': 4,
        'genius.com': 4, 'wikidata.org': 3, 'wikipedia.org': 3,
    }

    def __init__(self, search, fetch, llm=None, progress=print):
        self.search, self.fetch, self.llm, self.say = search, fetch, llm, progress

    def is_fact_query(self, q):
        l=q.lower()
        return any(k in l for k in (
            'من هو','من هي','ما هو','ما هي','معلومات عن','اعطيني معلومة',
            'معلومة عن','من يغني','متى','أين','كم','who is','what is',
            'song','اغنية','أغنية','فنان','مغني','مغنية','artist','singer'
        ))

    def _song_like(self,q):
        l=q.lower()
        return any(k in l for k in ('اغنية','أغنية','song','فنان','مغني','مغنية','artist','singer'))

    def _song_title(self,q):
        # Extract the likely title instead of searching the whole natural-language question.
        s=re.sub(r'[؟?!.,،:؛]',' ',q).strip()
        patterns=[
            r'(?:أغنية|اغنيه|اغنية|song)\s*["“”\']?(.+?)["“”\']?(?:\s+(?:لمن|من|لـ|ل|للفنان|للفنانة|للمغني|للمغنية|by)\b|$)',
            r'(?:فنان|فنانة|مغني|مغنية|artist|singer)\s+(?:أغنية|اغنية|song)\s*["“”\']?(.+?)\s*$',
        ]
        for p in patterns:
            m=re.search(p,s,flags=re.I)
            if m:
                title=m.group(1).strip(' "“”\'')
                # Remove common question tails.
                title=re.split(r'\s+(?:هو|هي|من|ما|ومين|ومن|؟|\?)\s*$',title,flags=re.I)[0].strip()
                if title:return title
        # English "artist of song X"
        m=re.search(r'(?:song)\s+["“”\']?([^"“”\']+)',s,flags=re.I)
        return m.group(1).strip() if m else ''

    def _queries(self,q):
        qs=[q]
        title=self._song_title(q) if self._song_like(q) else ''
        if title:
            qs += [
                f'"{title}" song artist',
                f'"{title}" "Apple Music"',
                f'"{title}" "Spotify"',
                f'"{title}" "Shazam"',
                f'"{title}" "YouTube"',
                f'"{title}" artist singer',
            ]
            # Independent domain-targeted searches are much less likely to
            # repeat the same scraped article.
            for d in ('music.apple.com','open.spotify.com','shazam.com','youtube.com'):
                qs.append(f'site:{d} "{title}"')
        out=[]
        for x in qs:
            x=x.strip()
            if x and x not in out:out.append(x)
        return out[:10]

    def _domain(self,url):
        try:
            h=urlparse(url).netloc.lower().split(':')[0]
            if h.startswith('www.'):h=h[4:]
            return h
        except Exception:return ''

    def _score(self,item,title=''):
        d=self._domain(item.get('url',''))
        score=self.TRUSTED_DOMAINS.get(d,0)
        blob=((item.get('title') or '')+' '+(item.get('snippet') or '')).lower()
        if title and title.lower() in blob:score+=2
        if any(x in blob for x in ('official','official audio','official music video')):score+=1
        return score

    def _collect(self,q):
        all_results=[];seen=set();successful=0
        title=self._song_title(q) if self._song_like(q) else ''
        for query in self._queries(q):
            try:r=self.search(query,10)
            except TypeError:r=self.search(query)
            except Exception:continue
            if r.get('success'):
                successful+=1
                for x in r.get('results',[]):
                    u=(x.get('url') or '').strip()
                    if not u or u in seen:continue
                    seen.add(u);all_results.append({**x,'search_query':query})
            if len(all_results)>=25:break
        all_results.sort(key=lambda x:self._score(x,title),reverse=True)
        return all_results[:10],successful,title

    def answer(self,q):
        self.say('🌐 البحث في الإنترنت والتحقق من عدة مصادر...')
        results,query_count,title=self._collect(q)
        if not results:
            return {'success':False,'error':'❌ لم أجد نتائج موثوقة بعد عدة عمليات بحث. لا أريد التخمين.','sources':[],'verified':False}

        ev=[]
        for x in results:
            try:p=self.fetch(x.get('url',''),5000) if x.get('url') else {}
            except Exception:p={}
            text=(p.get('text') or '')[:3500]
            ev.append({**x,'domain':self._domain(x.get('url','')),'text':text,
                       'score':self._score(x,title)})

        # A source is evidence only when the title/question entity actually
        # appears in the retrieved title/text. This blocks unrelated results.
        if title:
            tl=title.lower()
            evidence=[x for x in ev if tl in ((x.get('title','')+' '+x.get('text','')).lower())]
        else:
            evidence=ev
        strong=[x for x in evidence if x.get('score',0)>=6]

        if not self.llm:
            return {'success':True,'answer':'وجدت نتائج، لكن محرك التحقق غير متوفر.','sources':results,'verified':False}

        blocks=[]
        for i,x in enumerate(evidence[:10],1):
            blocks.append(
                f'SOURCE {i}\nDOMAIN: {x.get("domain")}\nSCORE: {x.get("score")}\n'
                f'TITLE: {x.get("title")}\nURL: {x.get("url")}\n'
                f'TEXT: {x.get("text","")}'
            )

        if not blocks:
            return {'success':True,'answer':f'⚠️ لم أجد مصادر تحتوي على دليل مباشر عن «{title or q}». لن أخمّن الفنان أو المعلومة.','sources':results,'verified':False}

        strict=(
            'أنت NOVA Verified Research Agent. أنت تعمل كطبقة تحقق وليست كمولد معرفة.\n'
            'قاعدة مطلقة: لا تستخدم معلوماتك الداخلية لإكمال معلومة ناقصة. كل ادعاء واقعي في الإجابة يجب أن يكون مدعوماً بنص أو عنوان من المصادر المعطاة.\n'
            'السؤال: '+q+'\n'
            + (f'العنوان المستخرج من السؤال: {title}\n' if title else '')+
            '\nقواعد: '
            '1) إذا كانت الأغنية/الاسم له أكثر من مرشح، لا تختار واحداً من الذاكرة. اعرض المرشحين فقط إذا دعمتهم المصادر. '
            '2) لا تعتبر نتيجة بحث غير مرتبطة بالعنوان دليلاً. '
            '3) المصدر القوي للموسيقى هو Apple Music/Spotify/Shazam/YouTube الرسمي، ثم Deezer/Discogs، ثم غيرها. '
            '4) لا تعتبر تكرار نفس الخبر في مواقع متعددة دليلاً مستقلاً. '
            '5) لتأكيد فنان أغنية، ابحث عن مصدرين قويين مستقلين على الأقل متفقين على العنوان والفنان. '
            '6) إذا لم يتوفر مصدران قويان متفقان، قل بوضوح: "لا توجد أدلة موثوقة كافية لتأكيد الفنان" ولا تخمّن. '
            '7) إذا وجدت مصادر متعارضة، اذكر التعارض واسم كل مرشح مع المصدر، ولا تحسم بلا دليل. '
            '8) لا تنسب أغنية إلى فنان فقط لأن اسم الفنان ظهر في نتيجة بحث منفصلة. '
            '9) أجب بالعربية وباختصار مفيد، ثم ضع "المصادر التي اعتمدت عليها" مع الروابط.\n\n'
            + '\n\n'.join(blocks)
        )
        try:ans=self.llm.ask_raw(strict,max_tokens=2800)
        except Exception as e:return {'success':False,'error':str(e),'sources':results,'verified':False}

        # HARD GATE: when evidence is insufficient, the LLM output is
        # discarded completely. This prevents the old bug where NOVA said
        # 'I could not verify' and then appended an invented biography.
        strong_domains={x.get('domain') for x in strong if x.get('domain')}
        has_two=len(strong_domains)>=2
        says_uncertain=any(k in ans.lower() for k in ('لا توجد أدلة','غير مؤكد','لا أستطيع تأكيد','غامض','غير كاف','insufficient','uncertain'))
        verified=has_two and not says_uncertain
        if not has_two:
            safe=(
                '⚠️ **لم أجد مصدرين موثوقين مستقلين كافيين لتأكيد هذه المعلومة، لذلك لن أخمّن.**\n\n'
                'لن أعرض معلومات إضافية غير مثبتة من نتائج البحث الحالية.'
            )
            return {'success':True,'answer':safe,'sources':results,'verified':False,
                    'strong_sources':len(strong),'independent_strong_domains':len(strong_domains),
                    'queries_used':query_count,'entity':title}
        return {'success':True,'answer':ans,'sources':results,'verified':verified,
                'strong_sources':len(strong),'independent_strong_domains':len(strong_domains),
                'queries_used':query_count,'entity':title}

# V8.0 deterministic fallback: source-grounded summaries only.
def _v8_answer_grounded(self,q):
    self.say('🌐 البحث في الإنترنت والتحقق من عدة مصادر...')
    try:
        results,query_count,title=self._collect(q)
    except Exception:
        results,query_count,title=[],0,''
    if not results:
        return '⚠️ لم أجد مصادر كافية للإجابة، ولن أخمّن.'
    # Only use distinct destination domains. Search-engine duplicates do not count.
    rows=[]; seen=set()
    for x in results:
        u=x.get('url',''); d=self._domain(u)
        if not d or d in seen: continue
        seen.add(d)
        text=''
        try:
            p=self.fetch(u,5000) if u else {}
            text=(p.get('text') or '')[:4500]
        except Exception: pass
        rows.append((x,d,text))
    strong=[r for r in rows if self.TRUSTED_DOMAINS.get(r[1],0)>=6]
    if len(strong)<2:
        return '⚠️ لم أجد مصدرين موثوقين مستقلين كافيين لتأكيد هذه المعلومة، لذلك لن أخمّن.'
    # For identity questions, provide only facts directly visible in the source titles/text.
    name=title or q
    snippets=[]
    for x,d,text in strong[:4]:
        visible=(x.get('title') or '')+' '+(x.get('snippet') or '')+' '+text
        low=visible.lower()
        if name.lower() in low or any(tok.lower() in low for tok in name.split() if len(tok)>2):
            snippets.append((d,x.get('title',''),x.get('url',''),visible))
    if len(snippets)<2:
        return '⚠️ وجدت مصادر، لكن لم أجد فيها دليلًا مباشرًا كافيًا على هوية الشخص/المعلومة. لن أخمّن.'
    lines=[f'🔎 وجدت معلومات مباشرة عن **{name}** في مصادر مستقلة:', '']
    for d,st,u,visible in snippets[:3]:
        # Do not synthesize biography facts. Report only the source identity and direct context.
        compact=re.sub(r'\s+',' ',visible).strip()
        if len(compact)>260: compact=compact[:257]+'...'
        lines.append(f'• **{d}** — {st}\n  {compact}\n  {u}')
    lines.append('\n⚠️ لم أضف معلومات مثل تاريخ الميلاد أو الجنسية أو المهنة إلا إذا كانت مثبتة مباشرة في المصادر.')
    return '\n'.join(lines)

VerifiedWeb.answer_grounded=_v8_answer_grounded
