# -*- coding: utf-8 -*-
"""核对覆盖、链接、代表集、公开全文许可与可复用题录。"""
import pathlib,json,re,urllib.parse,collections,hashlib
P=pathlib.Path(__file__).resolve().parents[1];xs=json.loads((P/'catalog/papers.json').read_text());mp=json.loads((P/'catalog/representative_map.json').read_text());mf=json.loads((P/'catalog/fulltext_manifest.json').read_text());st=json.loads((P/'catalog/stats.json').read_text());ids={x['id'] for x in xs};reps={r['id'] for r in mp['representatives']}
assert len(xs)==len(ids)==st['total']==438
assert len({x['doi'].lower() for x in xs if x['doi']})==len([x for x in xs if x['doi']])
assert len(reps)==st['representatives']==85
assert len(mp['technical_axes'])==st['technical_axes']==39 and len(mp['viewpoint_axes'])==st['viewpoint_axes']==23
for axis in mp['technical_axes']+mp['viewpoint_axes']:
 assert axis['anchors'] and set(axis['anchors'])<=reps
 assert set(axis['contrasts'])<=ids
assert 'F055' not in reps
for fid in reps:assert any('\u4e00'<=c<='\u9fff' for c in next(x for x in xs if x['id']==fid)['title_zh'])
pdfs=[]
for r in mf:
 if r['status']=='pdf_downloaded':
  p=P/r['path'];assert p.exists();assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];assert r['public_redistribution']['license_urls'];pdfs.append(p)
assert len(pdfs)==len(list((P/'papers/pdf').glob('*.pdf')))==st['public_pdfs']
files=[P/'README.md']+list((P/'docs').glob('*.md'))+list((P/'categories').glob('*.md'))+list((P/'papers').glob('*.md'))+[P/'catalog/ALL_PAPERS.md',P/'catalog/FULLTEXT_STATUS.md']
errors=[]
for f in files:
 for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',f.read_text()):
  if target.startswith(('http://','https://','#','mailto:')):continue
  if not (f.parent/urllib.parse.unquote(target.split('#')[0])).resolve().exists():errors.append((str(f.relative_to(P)),target))
assert not errors,errors[:10]
assert len(list((P/'papers').glob('F*.md')))==438
assert len(re.findall(r'^@\w+\{',(P/'catalog/references.bib').read_text(),re.M))==438
assert '先读15篇' not in (P/'README.md').read_text().replace('不再固定“先读15篇”','')
result={'题录数':438,'代表论文数':85,'技术路线数':39,'观点争议数':23,'所有覆盖行都有代表锚点':True,'所有本地阅读链接可解析':True,'代表论文均有中文导读':True,'公开全文数':len(pdfs),'公开全文都有许可依据且哈希匹配':True,'引用条目数':438,'模拟蓝图未列入实证代表':True,'公开历史要求':'公开推送前从已检查文件树建立干净提交；私有旧版本保留本地恢复存档'}
(P/'catalog/repository_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
