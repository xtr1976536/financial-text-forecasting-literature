# -*- coding: utf-8 -*-
import pathlib,json,shutil,re
P=pathlib.Path(__file__).resolve().parents[1];mf=json.loads((P/'catalog/fulltext_manifest.json').read_text());xs=json.loads((P/'catalog/papers.json').read_text());idx={x['id']:x for x in xs}
private=P/'.private_archive';private.mkdir(exist_ok=True)
if not (private/'original_fulltext_manifest.json').exists():(private/'original_fulltext_manifest.json').write_text(json.dumps(mf,ensure_ascii=False,indent=2))
a={r['id']:r for r in json.loads((P/'catalog/arxiv_license_audit.json').read_text())};b={r['id']:r for r in json.loads((P/'catalog/pdf_license_text.json').read_text())};audit=[]
for r in mf:
 fid=r['id'];cc=[];basis='';source=''
 if r['status']=='pdf_downloaded':
  if a.get(fid,{}).get('license_urls'):
   cc=a[fid]['license_urls'];basis='arXiv原文页明确许可';source=a[fid]['license_page']
  elif b.get(fid,{}).get('explicit_license_urls'):
   cc=b[fid]['explicit_license_urls'];basis='PDF正文或链接注释明确许可';source=r['download_url']
  elif 'aclanthology.org/' in r.get('download_url','') and idx[fid]['doi'].lower().startswith(('10.18653/','10.3115/')):
   cc=['https://creativecommons.org/licenses/by/4.0/' if idx[fid]['date']>='2016' else 'https://creativecommons.org/licenses/by-nc-sa/3.0/'];basis='ACL自有材料公开使用政策';source='https://aclanthology.org/faq/copyright/'
  cc=[u for u in cc if re.match(r'https?://creativecommons.org/(?:licenses/(?:by|by-sa|by-nc|by-nc-sa|by-nd|by-nc-nd)/[1-4]\.0/?|publicdomain/zero/1\.0/?)$',u)]
  if cc:
   r['public_redistribution']={'license_urls':cc,'evidence':basis,'evidence_url':source,'attribution':'作者、题名、原文、下载来源和许可均在对应阅读卡中保留；PDF原样提供；非商业研究文献库。'}
   audit.append({'id':fid,'public_pdf':True,**r['public_redistribution']})
  else:
   dest=private/'pdfs'/f'{fid}.pdf';dest.parent.mkdir(exist_ok=True)
   if (P/r['path']).exists():shutil.move(str(P/r['path']),str(dest))
   r.pop('path',None);r['status']='link_only';r['reason']='原已取得个人研究副本，但未确认公开转载许可；公开仓库仅提供原文入口，本地副本保留。';r['personal_copy_retained']=True
   audit.append({'id':fid,'public_pdf':False,'reason':'未确认公开转载许可；保留原文链接和本地个人副本。'})
(P/'catalog/fulltext_manifest.json').write_text(json.dumps(mf,ensure_ascii=False,indent=2));(P/'catalog/public_pdf_licenses.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print('公开PDF',sum(r['public_pdf'] for r in audit),'本地个人副本',sum(not r['public_pdf'] for r in audit))
