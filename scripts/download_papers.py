import pathlib,json,re,html,requests,concurrent.futures,hashlib,time,threading
P=pathlib.Path(__file__).resolve().parents[1];xs=json.loads((P/'catalog/papers.json').read_text());OA={};OT={}
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
for f in (P/'literature_review/raw').glob('openalex_*.json'):
 for x in json.loads(f.read_text()).get('results',[]):
  ds=[(x.get('doi')or'').replace('https://doi.org/','').lower()];ls=[l for l in x.get('locations',[]) if l]
  if x.get('best_oa_location'):ls.insert(0,x['best_oa_location'])
  for d in ds:
   if d:OA.setdefault(d,[]).extend(ls)
  OT.setdefault(norm(x.get('title')or''),[]).extend(ls)
manual={
'F036':['https://www.uts.edu.au/globalassets/sites/default/files/adg_cons2015_tetlock-journal-of-finance-2007.pdf'],
'F034':['https://www.uts.edu.au/globalassets/sites/default/files/adg_cons2015_loughran-mcdonald-je-2011.pdf'],
'F033':['https://www.nber.org/system/files/working_papers/w26186/w26186.pdf'],
'F421':['https://papers.nips.cc/paper/2023/file/86c17de05579cde52025f9984e6e2ebb-Paper-Conference.pdf'],
'F422':['https://proceedings.iclr.cc/paper_files/paper/2024/file/5132940b1bced8a7b28e9695d49d435a-Paper-Conference.pdf'],
'F423':['https://proceedings.nips.cc/paper_files/paper/2024/file/6ed5bf446f59e2c6646d23058c86424b-Paper-Conference.pdf'],
'F427':['https://ojs.aaai.org/index.php/AAAI/article/download/30383/32447'],
'F020':['https://aclanthology.org/2025.ijcnlp-long.54.pdf'],
'F028':['https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/jae.3095'],
'F002':['https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/ijfe.70239']}
core=['F036','F034','F033','F028','F002','F004','F021','F020','F023','F025','F016','F012','F421','F422','F423']
cache=P/'catalog/download_attempts';cache.mkdir(exist_ok=True);(P/'papers/pdf').mkdir(parents=True,exist_ok=True)
def candidates(x):
 arr=[{'url':u,'basis':'publisher/author/institution source','version':'see source','license':None} for u in manual.get(x['id'],[])]
 for d in [x['doi']]+x.get('alternative_dois',[]):
  if 'arxiv.' in d:arr.append({'url':'https://arxiv.org/pdf/'+d.split('arxiv.')[-1],'basis':'arXiv','version':'latest at retrieval 2026-10-28','license':'see arXiv source'})
 locs=OA.get(x['doi'],[])+OT.get(norm(x['title']),[])
 for l in locs:
  u=l.get('pdf_url')
  if u and (l.get('is_oa') or l.get('source',{}).get('is_oa') if l.get('source') else l.get('is_oa')):
   arr.append({'url':u,'basis':'OpenAlex open-access location','version':l.get('version'),'license':l.get('license')})
 d=x['doi']
 if d.startswith(('10.18653/v1/','10.3115/v1/')):arr.append({'url':'https://aclanthology.org/'+d.split('/v1/')[-1]+'.pdf','basis':'ACL Anthology','version':'published','license':'see source'})
 if d.startswith('10.3386/'):arr.append({'url':'https://www.nber.org/system/files/working_papers/'+d.split('/')[-1]+'/'+d.split('/')[-1]+'.pdf','basis':'NBER','version':'working paper','license':None})
 if d.startswith('10.1371/'):arr.append({'url':'https://journals.plos.org/plosone/article/file?id='+d+'&type=printable','basis':'PLOS publisher','version':'published','license':'see source'})
 if d.startswith('10.3390/'):
  suf=d.split('/')[-1];arr.append({'url':'https://www.mdpi.com/'+d+'/pdf','basis':'MDPI publisher','version':'published','license':'see source'})
 # Keep bounded attempts; no mirrors or authentication bypass.
 seen=set();out=[]
 for c in arr:
  if c['url'] in seen:continue
  seen.add(c['url']);c['url']=c['url'].replace('http://arxiv.org','https://arxiv.org');out.append(c)
 return out[:5 if x['id'] in core else 3]
def run(x):
 fid=x['id'];cfile=cache/(fid+'.json');dest=P/'papers/pdf'/(fid+'.pdf')
 if cfile.exists():
  old=json.loads(cfile.read_text())
  if old.get('status')=='pdf_downloaded' and dest.exists():return old
 opts=candidates(x);res={'id':fid,'title':x['title'],'doi':x['doi'],'landing_url':x['url'],'status':'link_only','attempts':[],'retrieved':'2026-10-28'}
 for c in opts:
  try:
   r=requests.get(c['url'],timeout=(8,22),headers={'User-Agent':'Mozilla/5.0 (compatible; LiteratureArchive/1.0)'},stream=True);r.raise_for_status()
   data=bytearray()
   for b in r.iter_content(65536):
    data.extend(b)
    if len(data)>25*1024*1024:raise ValueError('over 25 MiB per-file cap')
   if not bytes(data[:1024]).lstrip().startswith(b'%PDF'):raise ValueError('response is not a PDF')
   dest.write_bytes(data);res.update(status='pdf_downloaded',path='papers/pdf/'+fid+'.pdf',download_url=r.url,source_basis=c['basis'],version=c['version'],license=c['license'],bytes=len(data),sha256=hashlib.sha256(data).hexdigest());break
  except Exception as e:res['attempts'].append({'url':c['url'],'error':str(e)[:220]})
 if not opts:res['reason']='No direct openly accessible PDF URL in available metadata; original landing link retained.'
 elif res['status']=='link_only':res['reason']='Direct open-source PDF attempts blocked, unavailable, or not a PDF; original landing link retained.'
 cfile.write_text(json.dumps(res,ensure_ascii=False,indent=2));return res
ordered=sorted(xs,key=lambda x:x['id'] not in core)
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for r in ex.map(run,ordered):
  results.append(r);print(r['id'],r['status'],r.get('bytes',0),flush=True)
results.sort(key=lambda x:x['id']);(P/'catalog/fulltext_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('PDF',sum(r['status']=='pdf_downloaded' for r in results),'TOTAL',len(results),flush=True)
