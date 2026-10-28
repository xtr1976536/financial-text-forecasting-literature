import pathlib,json,requests,concurrent.futures,re,hashlib,urllib.parse
P=pathlib.Path(__file__).resolve().parents[1];rs=json.loads((P/'catalog/fulltext_manifest.json').read_text());lookup={r['doi']:r for r in rs};missing=[r for r in rs if r['status']=='link_only'];queries=[missing[i:i+40] for i in range(0,len(missing),40)]
raw=P/'catalog/fulltext_discovery';raw.mkdir(exist_ok=True)
def fetch(pair):
 i,part=pair;f=raw/f'openalex_batch_{i}.json'
 try:
  r=requests.get('https://api.openalex.org/works',params={'filter':'doi:'+'|'.join('https://doi.org/'+p['doi'] for p in part),'per-page':100},timeout=45);r.raise_for_status();f.write_text(json.dumps(r.json(),ensure_ascii=False));return r.json().get('results',[])
 except Exception as e:print('metadata',i,str(e)[:150],flush=True);return []
more=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for a in ex.map(fetch,enumerate(queries)):more.extend(a)
jobs=[]
for m in more:
 doi=(m.get('doi')or'').replace('https://doi.org/','').lower();rec=lookup.get(doi)
 if not rec:continue
 locs=[l for l in m.get('locations',[]) if l and l.get('is_oa')];urls=[]
 for l in locs:
  if l.get('pdf_url'):urls.append((l['pdf_url'],l.get('version'),l.get('license')))
 if urls:jobs.append((rec,urls[:3]))
 # Save repository landing candidates for targeted follow-up.
 rec['additional_oa_landings']=[l.get('landing_page_url') for l in locs if l.get('landing_page_url')]

def download(job):
 rec,urls=job;fid=rec['id']
 for u,version,license in urls:
  if any(a['url']==u for a in rec.get('attempts',[])):continue
  try:
   r=requests.get(u,timeout=(8,20),headers={'User-Agent':'Mozilla/5.0'},stream=True);r.raise_for_status();data=bytearray()
   for chunk in r.iter_content(65536):
    data.extend(chunk)
    if len(data)>25*1024**2:raise ValueError('file size cap')
   if not bytes(data[:1024]).lstrip().startswith(b'%PDF'):raise ValueError('not PDF')
   path=P/'papers/pdf'/f'{fid}.pdf';path.write_bytes(data);rec.update(status='pdf_downloaded',path=f'papers/pdf/{fid}.pdf',download_url=r.url,source_basis='OpenAlex direct open-access location (second discovery)',version=version,license=license,bytes=len(data),sha256=hashlib.sha256(data).hexdigest());print(fid,'added',len(data),flush=True);break
  except Exception as e:rec.setdefault('attempts',[]).append({'url':u,'error':str(e)[:180]})
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for r in ex.map(download,jobs):lookup[r['doi']]=r
(P/'catalog/fulltext_manifest.json').write_text(json.dumps(list(lookup.values()),ensure_ascii=False,indent=2));print('PDF',sum(r['status']=='pdf_downloaded' for r in lookup.values()),'TOTAL',len(lookup),flush=True)
