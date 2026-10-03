import re, urllib.parse, urllib.request, html

UA='Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/128 Mobile Safari/537.36 NOVA-AI/8.2'

def _fetch(url,timeout=5):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Language':'en-US,en;q=0.9,ar;q=0.8'})
    return urllib.request.urlopen(req,timeout=timeout).read().decode('utf-8','ignore')

def _parse_ddg(page,max_results):
    out=[]
    # DDG markup changes; capture result blocks without assuming attribute order.
    blocks=re.findall(r'<div[^>]+class=["\'][^"\']*result[^"\']*["\'][^>]*>.*?</div>\s*</div>',page,re.S|re.I)
    for block in blocks:
        m=re.search(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*class=["\'][^"\']*result__a[^"\']*["\']|<a[^>]+class=["\'][^"\']*result__a[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',block,re.S|re.I)
        if not m: continue
        href=html.unescape(m.group(1) or m.group(2)); title=clean(re.sub(r'<.*?>',' ',re.search(r'<a[^>]*result__a[^>]*>(.*?)</a>',block,re.S|re.I).group(1))) if re.search(r'<a[^>]*result__a[^>]*>(.*?)</a>',block,re.S|re.I) else ''
        sm=re.search(r'class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>(.*?)</',block,re.S|re.I)
        snippet=clean(sm.group(1)) if sm else ''
        if href.startswith('//'): href='https:'+href
        if href and title: out.append({'title':title,'url':href,'snippet':snippet})
        if len(out)>=max_results: break
    return out

def _parse_bing(page,max_results):
    out=[]
    for m in re.finditer(r'<li[^>]*class=["\']b_algo["\'][^>]*>.*?<h2[^>]*>\s*<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',page,re.S|re.I):
        href=html.unescape(m.group(1)); title=clean(m.group(2))
        block=m.group(0)
        sm=re.search(r'<p[^>]*>(.*?)</p>',block,re.S|re.I)
        snippet=clean(sm.group(1)) if sm else ''
        out.append({'title':title,'url':href,'snippet':snippet})
        if len(out)>=max_results:break
    return out

def _parse_google(page,max_results):
    out=[]
    # Lightweight fallback; Google markup changes often, so this is best-effort.
    for m in re.finditer(r'<a href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>',page,re.S|re.I):
        href=html.unescape(m.group(1)); title=clean(m.group(2))
        if not title or len(title)<3:continue
        if any(x in href for x in ('google.com/search','accounts.google','support.google')):continue
        out.append({'title':title,'url':href,'snippet':''})
        if len(out)>=max_results:break
    return out

def search_web(query,max_results=6):
    query=str(query).strip()
    if not query:return {'success':False,'error':'اكتب ما تريد البحث عنه.','results':[]}
    encoded=urllib.parse.urlencode({'q':query})
    endpoints=[
        ('ddg','https://html.duckduckgo.com/html/?'+encoded,_parse_ddg),
        ('bing','https://www.bing.com/search?'+encoded,_parse_bing),
    ]
    errors=[]
    merged=[];seen=set()
    for name,url,parser in endpoints:
        try:
            page=_fetch(url)
            results=parser(page,max_results)
            for x in results:
                u=x.get('url','')
                if u and u not in seen:
                    seen.add(u);merged.append(x)
            # Always query both engines; otherwise the first engine can
            # monopolize the result set (often Spotify for music queries).
        except Exception as e: errors.append(name+': '+str(e))
    return {'success':bool(merged),'query':query,'results':merged[:max_results], 'error':'' if merged else '; '.join(errors) or 'لم أجد نتائج.'}

def fetch_page(url,max_chars=7000):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':UA})
        raw=urllib.request.urlopen(req,timeout=5).read().decode('utf-8','ignore')
        raw=re.sub(r'<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>',' ',raw,flags=re.I|re.S)
        return {'success':True,'text':clean(raw)[:max_chars]}
    except Exception as e:return {'success':False,'text':'','error':str(e)}

def clean(s):return re.sub(r'\s+',' ',re.sub('<[^>]+>','',html.unescape(s))).strip()
