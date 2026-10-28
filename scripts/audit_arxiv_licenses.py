# -*- coding: utf-8 -*-
import pathlib,json,requests,concurrent.futures,re
P=pathlib.Path(__file__).resolve().parents[1];rs=json.loads((P/'catalog/fulltext_manifest.json').read_text());jobs=[]
for r in rs:
 if r['status']=='pdf_downloaded' and ('arxiv.org/' in r.get('download_url','') or r.get('license')=='see arXiv source'):
  aid=r.get('download_url','').split('/')[-1];aid=re.sub(r'v\d+$','',aid).replace('.pdf','');jobs.append((r['id'],aid))
def run(job):
 fid,aid=job;p=P/'.private_archive/license_sources'/f'{fid}.html'
 try:
  if p.exists():s=p.read_text()
  else:
   r=requests.get('https://arxiv.org/abs/'+aid,timeout=25);r.raise_for_status();s=r.text;p.write_text(s)
  urls=re.findall(r'https?://(?:creativecommons.org|arxiv.org/licenses|arxiv.org/abs|info.arxiv.org/help/license)[^"\s<>]*',s)
  cc=[u for u in urls if 'creativecommons.org/' in u]
  return {'id':fid,'license_page':'https://arxiv.org/abs/'+aid,'license_urls':sorted(set(cc)),'status':'explicit_cc' if cc else 'not_confirmed'}
 except Exception as e:return {'id':fid,'license_page':'https://arxiv.org/abs/'+aid,'status':'not_confirmed','error':str(e)[:120]}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:out=list(ex.map(run,jobs))
(P/'catalog/arxiv_license_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('checked',len(out),'explicit CC',sum(r['status']=='explicit_cc' for r in out))
