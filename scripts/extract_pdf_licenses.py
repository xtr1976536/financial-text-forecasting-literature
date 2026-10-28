# -*- coding: utf-8 -*-
import pathlib,json,re
from pypdf import PdfReader
P=pathlib.Path(__file__).resolve().parents[1];out=[]
for f in (P/'papers/pdf').glob('*.pdf'):
 try:
  r=PdfReader(f);s=' '.join(p.extract_text() or '' for p in list(r.pages[:3])+list(r.pages[-1:])); links=[]
  for page in list(r.pages[:3])+list(r.pages[-1:]):
   for ann in page.get('/Annots',[]):
    a=ann.get_object().get('/A',{})
    if a.get('/URI'):links.append(str(a['/URI']))
  s+=' '+' '.join(links);urls=re.findall(r'https?\s*:\s*//\s*creativecommons\.org\s*/\s*(?:licenses\s*/\s*[a-z\s-]+\s*/\s*[0-9.]+|publicdomain\s*/\s*zero\s*/\s*[0-9.]+)',s,re.I);urls=[re.sub(r'\s+','',u).rstrip('.') for u in urls]
  out.append({'id':f.stem,'explicit_license_urls':sorted(set(urls)),'license_text_present':bool(re.search(r'creative commons.{0,100}(?:attribution|license)',s,re.I))})
 except Exception as e:out.append({'id':f.stem,'error':str(e)[:150]})
(P/'catalog/pdf_license_text.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('PDFs',len(out),'explicit',sum(bool(x.get('explicit_license_urls')) for x in out))
