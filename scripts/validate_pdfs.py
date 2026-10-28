import json,pathlib,re,unicodedata,collections
from pypdf import PdfReader
P=pathlib.Path(__file__).resolve().parents[1];xs={x['id']:x for x in json.loads((P/'catalog/papers.json').read_text())};results=[]
stop={'the','a','an','of','and','for','to','in','with','using','from','on','by','is','as','based','its','via','at'}
def words(s):return set(re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()))-stop
for f in sorted((P/'papers/pdf').glob('*.pdf')):
 try:
  reader=PdfReader(f);text=' '.join(page.extract_text() or '' for page in reader.pages[:3]);x=xs[f.stem];target=words(x['title']);actual=words(text);ratio=len(target&actual)/max(1,len(target));status='title_overlap_pass' if ratio>=.65 else 'manual_check_needed'
  result={'id':f.stem,'pages':len(reader.pages),'bytes':f.stat().st_size,'title_token_coverage':round(ratio,3),'status':status}
  if status!='title_overlap_pass':result['opening_text']=text[:800]
  results.append(result)
 except Exception as e:results.append({'id':f.stem,'status':'invalid_pdf','error':str(e)[:300]})
(P/'catalog/pdf_validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(collections.Counter(r['status'] for r in results));print(json.dumps([r for r in results if r['status']!='title_overlap_pass'],ensure_ascii=False,indent=2))
