# -*- coding: utf-8 -*-
import json,pathlib,requests,xml.etree.ElementTree as ET,concurrent.futures,re
P=pathlib.Path(__file__).resolve().parents[1];xs=json.loads((P/'catalog/papers.json').read_text());mf=json.loads((P/'catalog/fulltext_manifest.json').read_text());ns={'a':'http://www.w3.org/2005/Atom'}
items=[('F429','1712.02136','WSDM 2018','倾听混乱的低语：面向新闻的股票趋势预测','新闻层级注意力、自步学习与噪声过滤。'),('F430','2310.01728','ICLR 2024','通过重编程大语言模型进行时间序列预测','数值片段与文本原型重编程，冻结语言模型主干。'),('F431','2403.07815','TMLR 2024','Chronos：学习时间序列的语言','缩放和量化后的数值 token 概率建模；语言架构不等于文本增量。'),('F432','2310.07820','NeurIPS 2023','大语言模型是零样本时间序列预测器','数字字符串、分词与概率密度映射的零样本路线。'),('F433','2402.18485','KDD 2024','金融交易多模态基础智能体','工具、记忆检索、反思与行动组成的交易系统。'),('F434','2311.13743','AAAI Symposium 2024；另有2025期刊扩展','FinMem：分层记忆与角色设计的交易智能体','按信息时效和重要性组织记忆，服务交易决策。'),('F437','2305.08524','arXiv 2023','衡量基于文本的金融预测模型的一致性','FinTrust 以语义保持扰动检验金融文本预测的稳定性。')]
p=P/'catalog/representative_supplement_arxiv.xml'
if not p.exists():
 r=requests.get('https://export.arxiv.org/api/query',params={'id_list':','.join(i[1] for i in items),'max_results':20},timeout=45);r.raise_for_status();p.write_text(r.text)
lookup={e.findtext('a:id',namespaces=ns).split('/abs/')[-1].split('v')[0]:e for e in ET.fromstring(p.read_text()).findall('a:entry',ns)}
new=[]
for fid,aid,venue,zh,finding in items:
 e=lookup[aid];new.append(dict(id=fid,title=' '.join(e.findtext('a:title',namespaces=ns).split()),title_zh=zh,doi='10.48550/arxiv.'+aid,date=e.findtext('a:published',namespaces=ns)[:10],authors='; '.join(a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)),venue=venue,url='https://arxiv.org/abs/'+aid,alternative_dois=[],sources=['catalog/representative_supplement_arxiv.xml'],scope='补充的技术或观点代表',tags=['代表性补检'],read_level='原始摘要与方法定位核读',publication_status='预印本入口；会议信息见来源字段',curated_note={'finding':finding,'caveat':'用于代表该路线，未独立复现；通用预测或组合结果不等于文本相对强数值基准的增量。'},verification_status='arXiv API核对题名作者日期',date_precision='日'))
# Three records use publisher Crossref metadata; source-only IJCAI record below does not invent a DOI.
crs=[('F435','10.1093/qje/qjw024','经济政策不确定性的测量','新闻词频构建经济政策不确定性指数，代表可解释经济概念测量。'),('F436','10.1016/j.jfineco.2018.12.009','新闻及其语境如何影响全球风险与收益','主题情绪、频率与异常性共同刻画新闻；跨国家、时期和预测期异质性。'),]
# Confirm exact DOI for global-context paper through title search rather than trusting recalled identifier.
r=requests.get('https://api.crossref.org/works',params={'query.title':'How news and its context drive risk and returns around the world','rows':3},timeout=30);r.raise_for_status()
for m in r.json()['message']['items']:
 if re.sub('[^a-z]','',m.get('title',[''])[0].lower())=='hownewsanditscontextdriveriskandreturnsaroundtheworld':crs[1]=(crs[1][0],m['DOI'],crs[1][2],crs[1][3]);break
for fid,doi,zh,finding in crs:
 p=P/'catalog'/f'{fid}_source.json'
 if p.exists():m=json.loads(p.read_text())['message']
 else:
  r=requests.get('https://api.crossref.org/works/'+doi,timeout=30);r.raise_for_status();p.write_text(json.dumps(r.json(),ensure_ascii=False,indent=2));m=r.json()['message']
 parts=m.get('published',m.get('issued',{})).get('date-parts',[[2016]])[0];date='-'.join(str(v) if i==0 else str(v).zfill(2) for i,v in enumerate(parts))
 new.append(dict(id=fid,title=m['title'][0],title_zh=zh,doi=m['DOI'].lower(),date=date,authors='; '.join((a.get('given','')+' '+a.get('family','')).strip() for a in m.get('author',[])),venue='; '.join(m.get('container-title',[])),url=m.get('URL','https://doi.org/'+doi),alternative_dois=[],sources=[f'catalog/{fid}_source.json'],scope='补充的技术或观点代表',tags=['代表性补检'],read_level='出版方或作者机构摘要核读',publication_status='出版论文',curated_note={'finding':finding,'caveat':'历史结果依样本与信息集而变；用于路线定位，不宣称普遍因果效应或现代市场稳健盈利。'},verification_status='Crossref单DOI及来源题名核对',date_precision='日' if len(parts)==3 else '年'))
new.append(dict(id='F438',title='Knowledge-Driven Event Embedding for Stock Prediction',title_zh='用于股票预测的知识驱动事件嵌入',doi='10.18653/v1/C16-1201',date='2016-12',authors='Xiao Ding; Yue Zhang; Ting Liu; Junwen Duan',venue='COLING 2016',url='https://aclanthology.org/C16-1201/',alternative_dois=[],sources=['https://aclanthology.org/C16-1201/'],scope='补充的技术或观点代表',tags=['事件表示','知识图谱'],read_level='会议原文摘要核读',publication_status='会议出版论文',curated_note={'finding':'把外部知识图谱纳入事件嵌入学习，代表事件语义与关系知识结合。','caveat':'会议页面 DOI 不声称 Crossref 注册核验；未独立复现。'},verification_status='ACL Anthology 官方页面核对',date_precision='月'))
new.append(dict(id='F428',title='Deep Learning for Event-Driven Stock Prediction',title_zh='事件驱动股票预测的深度学习',doi='',source_id='ijcai:2015/329',date='2015',authors='Xiao Ding; Yue Zhang; Ting Liu; Junwen Duan',venue='IJCAI 2015，2327–2332',url='https://ijcai.org/proceedings/2015/329',alternative_dois=[],sources=['https://ijcai.org/proceedings/2015/329'],scope='补充的技术或观点代表',tags=['事件表示','神经网络'],read_level='会议原文摘要与方法关键段落核读',publication_status='会议出版论文',curated_note={'finding':'事件元组、神经张量事件嵌入与多预测尺度CNN，代表早期事件语义路线。','caveat':'历史基准与模拟交易不等于当前可实现收益；来源未提供可核实DOI，因此不填。'},verification_status='IJCAI会议原文题名作者页码核对',date_precision='年'))
existing={x['id'] for x in xs}
for x in new:
 if x['id'] not in existing:xs.append(x);mf.append(dict(id=x['id'],title=x['title'],doi=x['doi'],landing_url=x['url'],status='link_only',reason='代表性补检，先提供原始来源；公开全文须核对转载许可。',attempts=[],retrieved='2026-10-28'))
xs.sort(key=lambda x:x['id']);mf.sort(key=lambda x:x['id']);(P/'catalog/papers.json').write_text(json.dumps(xs,ensure_ascii=False,indent=2));(P/'catalog/fulltext_manifest.json').write_text(json.dumps(mf,ensure_ascii=False,indent=2));print('total',len(xs),'new records',len(new))
