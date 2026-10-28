# -*- coding: utf-8 -*-
"""从统一元数据和覆盖矩阵生成中文阅读入口；不改变论文原文。"""
import pathlib,json,re,html,collections
P=pathlib.Path(__file__).resolve().parents[1]
xs=json.loads((P/'catalog/papers.json').read_text());mf={r['id']:r for r in json.loads((P/'catalog/fulltext_manifest.json').read_text())};mp=json.loads((P/'catalog/representative_map.json').read_text());reps={r['id']:r for r in mp['representatives']};idx={x['id']:x for x in xs};nt=len(mp['technical_axes']);nv=len(mp['viewpoint_axes']);nr=len(reps);npdf=sum(r['status']=='pdf_downloaded' for r in mf.values())
cats=[('01-incremental-value','文本增量：收益与价格'),('02-volatility-risk','波动率、尾部与财务风险'),('03-fusion-alignment','融合、对齐、事件与图结构'),('04-representation','词典、情绪、嵌入与叙事'),('05-evaluation-leakage','评估、泄漏、稳健性与反证'),('06-small-llms','小型语言模型与时序适配'),('07-benchmarks-surveys','数据集、基准与综述'),('08-macro-cross-assets','宏观、央行与跨资产'),('09-adjacent','智能体、决策与其他邻接研究')]
def classify(x):
 t=x['title'].lower();fid=x['id']
 if fid in {'F421','F422','F423','F424','F425','F426','F427','F430','F431','F432'}:return cats[5][0]
 if re.search(r'look.?ahead|lookahead|leakage|without hindsight|less information|availability contract|limits of|caution ahead|bias in the multimodal|adversarial attack|measuring consistency',t):return cats[4][0]
 if re.search(r'benchmark|dataset|survey|review|fnspid',t):return cats[6][0]
 if re.search(r'fusion|multimodal|multi.modal|cross.attention|interleaved|event representation|alignment|synergy|structured information|dialoguegat|voltage|echo.gl|event.driven|knowledge.driven event',t):return cats[2][0]
 if re.search(r'volatility|risk|distress|bankrupt|default',t):return cats[1][0]
 if re.search(r'macro|inflation|economic forecast|central bank|monetary|fomc|exchange rate|forex|bond|oil|commodity|cryptocurr|bitcoin|economic policy',t):return cats[7][0]
 if re.search(r'finbert|fingpt|sentiment analysis|text as data|textual analysis in finance|dictionary|narrative|topic|embedding',t):return cats[3][0]
 if re.search(r'agent|finmem|reinforcement|portfolio allocation',t):return cats[8][0]
 if re.search(r'stock|return|equity|asset|price|predict',t):return cats[0][0]
 return cats[8][0]
def title(x):return re.sub(r'\s+',' ',x['title']).replace('|','/').strip()
def label(fid):return idx[fid].get('title_zh') or '原文：'+title(idx[fid])
def refs(ids,prefix='../'):return '；'.join(f'[{fid}·{label(fid)}]({prefix}papers/{fid}.md)' for fid in ids)
def access(x,prefix='../'):
 r=mf[x['id']];a=[]
 if r['status']=='pdf_downloaded':a.append(f'[仓库全文]({prefix}{r["path"]})')
 a.append(f'[原文入口]({x["url"]})');return ' · '.join(a)
for x in xs:
 x['category']=classify(x);x['representative']=x['id'] in reps;x['fulltext_status']=mf[x['id']]['status'];x['pdf_path']=mf[x['id']].get('path');x.pop('core15',None)
 if x['id']=='F055':x['curated_note']={'finding':'提出时点检索、概率校准和选择性拒答的金融预测蓝图；原文明确只报告模拟结果。','caveat':'不作为真实市场有效性、收益改善或校准保证已成立的实证证据。'};x['read_level']='原文摘要核读：已识别模拟结果限制'
counts=collections.Counter(x['category'] for x in xs);(P/'catalog/papers.json').write_text(json.dumps(xs,ensure_ascii=False,indent=2))
for x in xs:
 fid=x['id'];r=mf[fid];n=x.get('curated_note');rep=reps.get(fid);zh=x.get('title_zh');heading=zh or f'{dict(cats)[x["category"]]}文献'
 lines=[f'# {fid} · {heading}','',f'[全部论文](../catalog/ALL_PAPERS.md) · [所属分类](../categories/{x["category"]}.md)'+(' · [代表性论文地图](../docs/代表性论文地图.md)' if rep else ''),'',f'**原文题名：** {title(x)}','',f'**作者：** {x["authors"]}','',f'**题录日期：** {x["date"]}；**刊物或来源：** {x["venue"]}','',f'**原文标识：** '+(f'[{x["doi"]}](https://doi.org/{x["doi"]})' if x['doi'] else x.get('source_id','见原文来源')),'',f'**阅读：** {access(x)}','','**全文状态：** '+('已存可公开转载的PDF；版本与许可见下方。' if r['status']=='pdf_downloaded' else ('原已获取个人研究副本；公开仓库只保留原文链接。' if r.get('personal_copy_retained') else '本仓库仅提供原文或公开版本入口；没有把链接写成已存全文。')),'',f'**本次核读层级：** {x["read_level"]}。','']
 if rep:lines+=['## 为什么具有代表性','',f'**定位：** {rep["role"]}。','',rep['why_selected'],'','**技术路线：** '+('、'.join(rep['anchor_axes']) or '见相关路线的对照论文')+'；**对照或观点位置：** '+('、'.join(rep['contrast_axes']) or '见技术与观点覆盖表')+'。','','“具有代表性”表示它清楚提出一种方法、测量或识别问题，不表示结论已被独立复现或可普遍外推。','']
 if n:lines+=['## 核读笔记','',n['finding'],'','**证据边界：** '+n['caveat'],'']
 else:lines+=['## 阅读状态','','已完成题名和元数据筛选；部分代表论文另参考原始摘要定位路线，但未据此编造样本量、增益或未核读的消融结论。请结合覆盖表中的阅读问题查原文。','']
 if r['status']=='pdf_downloaded':
  lic=r['public_redistribution'];lines+=['## 全文来源与许可','',f'- 下载来源：[{r.get("source_basis","原始来源")}]({r["download_url"]})',f'- 许可核对：[{lic["evidence"]}]({lic["evidence_url"]})','- 适用许可：'+'；'.join(f'[{u}]({u})' for u in lic['license_urls']),'- 作者、原始题名和来源见本页；PDF未修改。非商业研究文献库，不将全部论文统一重新授权。',f'- 文件校验值：`{r["sha256"]}`','']
 if x.get('alternative_dois'):lines+=['**合并版本：** '+'；'.join(f'[{d}](https://doi.org/{d})' for d in x['alternative_dois']),'']
 if x.get('crossref_publication_date'):lines+=[f'**出版日期提示：** Crossref字段为 {x["crossref_publication_date"]}；题录、在线、卷期和工作论文日期可能不同。','']
 (P/'papers'/f'{fid}.md').write_text('\n'.join(lines))
for f,name in cats:
 a=sorted([x for x in xs if x['category']==f],key=lambda x:(not x['representative'],-int(x['date'][:4]),x['id']))
 lines=[f'# {name}','', '[返回首页](../README.md) · [代表性论文地图](../docs/代表性论文地图.md)','',f'本类{len(a)}条；★表示按技术或观点选出的代表，不表示“已证实有效”。原始英文题名保留用于文献核对。','','|编号|日期|中文导读或原文题名|阅读|','|---|---|---|---|']
 for x in a:lines.append(f'|{"★ " if x["representative"] else ""}{x["id"]}|{x["date"]}|[{label(x["id"])}](../papers/{x["id"]}.md)|{access(x)}|')
 (P/'categories'/f'{f}.md').write_text('\n'.join(lines)+'\n')
lines=[f'# 全部{len(xs)}条论文','', '[返回首页](../README.md) · [代表性论文地图](../docs/代表性论文地图.md)','', 'F001–F420为初轮检索，F421–F427为小模型补查，F428–F438为代表性覆盖补检；稳定编号不代表阅读排名。中文为导读译名，正式引用请用单篇卡片中的原文题名。','','|编号|题录日期|中文导读或原文题名|主分类|阅读|','|---|---|---|---|---|']
for x in xs:lines.append(f'|{"★ " if x["representative"] else ""}{x["id"]}|{x["date"]}|[{label(x["id"])}](../papers/{x["id"]}.md)|[{dict(cats)[x["category"]]}](../categories/{x["category"]}.md)|{access(x)}|')
(P/'catalog/ALL_PAPERS.md').write_text('\n'.join(lines)+'\n')
# Two independent coverage matrices, each with anchor papers and a question.
for filename,key,heading in [('技术路线覆盖表.md','technical_axes','技术路线覆盖表'),('观点与争议覆盖表.md','viewpoint_axes','观点与争议覆盖表')]:
 lines=[f'# {heading}','', '[返回首页](../README.md) · [代表性论文地图](代表性论文地图.md) · [选取标准](选取标准与证据分层.md)','',mp['scope'],'','每行是一项覆盖义务：至少有一篇直接代表或方法锚点，并列出必要的反方、限制条件或补充路线。没有把同一论文反复出现计作不同研究。','','|编号|技术或观点|代表与锚点|反方、限制或补充|带着什么问题读|','|---|---|---|---|---|']
 for a in mp[key]:lines.append(f'|{a["code"]}|{a["name"]}|{refs(a["anchors"])}|{refs(a["contrasts"])}|{a["reading_point"]}|')
 lines+=['','## 覆盖检查','','本表所有行均有锚点，所有编号均能指向原始题录和阅读卡。主张方向、方法路线与证据成熟度分别记录；提到一种方法不等于认定其有效。','']
 if key=='technical_axes':lines+=['不确定性、拒答、因果和智能体方向需特别注意：有的论文只是设计蓝图或预测关联，并不提供真实市场效用或结构因果识别。F055只在补充列出现，不列入实证代表集。','']
 (P/'docs'/filename).write_text('\n'.join(lines))
lines=['# 代表性论文地图','', '[返回首页](../README.md) · [技术路线覆盖表](技术路线覆盖表.md) · [观点与争议覆盖表](观点与争议覆盖表.md) · [选取标准](选取标准与证据分层.md)','',f'从{len(xs)}条文献中提取 **{nr}篇代表论文**，覆盖 **{nt}条技术路线、{nv}组观点与争议**。不再规定“先读15篇”，也不要求按一条总排名阅读。','', '**使用方式：** 先选自己要解决的问题，再从对应覆盖表进入代表论文；先读锚点，再读同一行的反方或边界。若只看正面方法论文，容易把表示能力、同期解释和可交易增量混为一谈。','', '## 按研究问题进入','', '- 文本到底有没有增量：观点V01–V09；技术T01–T12。','- 文本应该怎样进入模型：技术T13–T28；观点V10–V11、V18–V22。','- 小模型为什么可能有效：技术T29–T34；观点V11–V15。','- 如何避免结果被评估方式驱动：技术T28、T34–T35；观点V13–V20。','', '## 经典和已发表方法代表','', '这些论文被选中是因为它们清楚定义了一条方法或经济问题；“已发表”不意味着可以跳过其数据和时点检查。','','|编号|中文导读名|代表什么|阅读|','|---|---|---|---|']
for r in mp['representatives']:
 if r['role']=='经典或已有发表的路线代表':lines.append(f'|{r["id"]}|[{r["title_zh"]}](../papers/{r["id"]}.md)|{r["why_selected"]}|{access(idx[r["id"]])}|')
lines+=['','## 近期针对性证据与争议观察','','这组论文回答身份捷径、日期对齐、污染、基准、条件信息等具体问题。它们不因新近就被称为经典；其中预印本、局部样本和未复现结果均需保留边界。','','|编号|中文导读名|代表什么|阅读|','|---|---|---|---|']
for r in mp['representatives']:
 if r['role']!='经典或已有发表的路线代表':lines.append(f'|{r["id"]}|[{r["title_zh"]}](../papers/{r["id"]}.md)|{r["why_selected"]}|{access(idx[r["id"]])}|')
lines+=['','## 不当作已验证实证的观察项','',f'- [F055·{label("F055")}](../papers/F055.md)：原文明确是模拟结果，只提供拒答与校准的设计蓝图；不作为金融预测或交易有效性的代表。','', '## 跨论文阅读卡','','每篇记录：目标与预测期；输入完整可得时点；数值基准；文本表示；融合方式；训练与调参边界；模型知识截止；身份和数量对照；样本外增益；依赖和多重检验；成本后效用；可复用设计。','']
(P/'docs/代表性论文地图.md').write_text('\n'.join(lines))
standards='''# 选取标准与证据分层

[返回首页](../README.md) · [代表性论文地图](代表性论文地图.md)

## 代表性的判断

优先选择明确提出一条方法或经济问题、后续工作反复参照、能够清楚区分机制和评价对象的论文。经典测量、早期方法、后续技术扩展、正面结果和反面诊断均可具有代表性。没有按引用量、期刊级别、模型规模或作者的性能宣称单独排名。

补检加入事件驱动预测、层级新闻注意力、知识事件嵌入、重编程、数值基础模型、零样本外推、交易智能体、经济不确定性及语义一致性等原清单遗漏的锚点。已有文献保留编号，不把同一研究的正式版和预印本重复计数。

## 两套独立覆盖轴

技术表回答“输入如何表示、怎样融合、如何训练和评价”；观点表回答“文本是否有增量、增益来自何处、何时失效及何种解释站不住”。一个问题可以需要多篇论文共同覆盖，一篇论文也可以覆盖多行。覆盖矩阵的全部锚点必须在代表集中；仅作为模拟蓝图的观察项例外且明确标注。

这里的“覆盖”是本轮金融文本预测检索范围内列出的主要路线和争议，不声称穷尽所有学科或未来技术。新发现一条未覆盖路线时，应增加一行并寻找直接代表，不能为固定篇数删掉它。

## 证据成熟度

- 经典或已有发表的方法代表：用于理解路线起源或可比较设计，不等同独立复现。
- 近期针对性证据或新路线观察：用于识别最新争议；预印本身份、样本与方法限制逐篇保留。
- 仅模拟或框架蓝图：不能证明真实市场有效性，不列作实证代表。

阅读深度是另一维度。题录核验、摘要核读、关键方法与结果检查、独立代码复现不可相互替代。本仓库没有声称已逐篇全文精读或独立复现所有代表论文。只有核对到的内容才能写成具体结论；不把“未读到”写成“作者没有做”。

## 结论使用边界

情绪标签准确、当期价格反应、未来预测、相对强数值基准的增量、成本后投资效用分别记录。技术中使用“因果”“注意力”“解释”等术语，不自动代表结构因果识别或忠实解释；需要相应研究设计支持。

公开文档的说明、导航、导读译名和阅读问题使用中文。英文原始题名、作者、刊名、代码标识和DOI保留原样，以便准确检索和正式引用；中文导读名不是出版方正式译名。
'''
(P/'docs/选取标准与证据分层.md').write_text(standards)
# Backward compatible old link, now just a Chinese signpost.
(P/'docs/CORE15.md').write_text('# 阅读入口已更新\n\n不再按固定篇数安排先读清单。请使用[代表性论文地图](代表性论文地图.md)、[技术路线覆盖表](技术路线覆盖表.md)和[观点与争议覆盖表](观点与争议覆盖表.md)。\n')
# Bibliography generated from current metadata, with missing DOI left genuinely missing.
b=[]
def esc(v):return str(v).replace('{','').replace('}','').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
for x in xs:
 fields={'title':'{'+esc(title(x))+'}','author':' and '.join(esc(a) for a in x['authors'].split('; ')),'year':x['date'][:4],'url':x['url'],'howpublished':esc(x['venue']),'note':x['id']+'；题录日期与正式卷期可能不同；检索日期2026-10-28'}
 if x['doi']:fields['doi']=x['doi']
 b.append('@misc{'+x['id']+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}')
(P/'catalog/references.bib').write_text('\n\n'.join(b)+'\n')
summary={'total':len(xs),'original':420,'small_model_supplement':7,'coverage_supplement':11,'representatives':nr,'technical_axes':nt,'viewpoint_axes':nv,'public_pdfs':npdf,'link_only':len(xs)-npdf,'categories':{name:counts[f] for f,name in cats},'as_of':'2026-10-28'};(P/'catalog/stats.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
readme=['# 金融文本与时序预测文献库','', '**阅读入口：[代表性论文地图](docs/代表性论文地图.md) · [技术路线覆盖表](docs/技术路线覆盖表.md) · [观点与争议覆盖表](docs/观点与争议覆盖表.md)**','', '研究问题：文本相对数值信息是否有稳定增量？应怎样表示并进入模型？小型语言模型是否足以形成有效预测？','',f'截至2026年10月28日，共 **{len(xs)}条文献**，从中提取 **{nr}篇代表论文**，覆盖 **{nt}条技术路线、{nv}组观点与争议**。数量服从覆盖需要，不再固定“先读15篇”。','', '## 怎样使用','', '1. 在技术表或观点表中选一个具体问题，先看锚点论文，再看同一行的反方或限制条件。','2. 打开单篇阅读卡，查看中文导读、原始题名、原文入口、核读层级和证据边界。','3. 正式引用使用原始题名与DOI；不要把中文导读名当作出版方译名。','',f'公开版保留 **{npdf}份已核对公开转载许可的PDF**，其余条目提供原始来源入口。公开前获得的个人阅读副本保留在本地，未确认转载许可的副本不放入公开版本。见[全文状态](catalog/FULLTEXT_STATUS.md)和[许可说明](docs/公开全文与引用说明.md)。','', '## 代表性论文入口','',f'- [代表性论文地图](docs/代表性论文地图.md)：{nr}篇，分别标注经典方法与近期观察，说明选取原因。',f'- [技术路线覆盖表](docs/技术路线覆盖表.md)：{nt}行，每行有代表、对照和阅读问题。',f'- [观点与争议覆盖表](docs/观点与争议覆盖表.md)：{nv}行，包含正面、负面和条件性发现。','- [选取标准与证据分层](docs/选取标准与证据分层.md)：代表性、成熟度、核读深度分开记录。','', '## 全部文献与资料','',f'- [全部{len(xs)}条论文](catalog/ALL_PAPERS.md)；每条都有独立阅读卡。','- [中文研究综述](literature_review/研究综述.md)与[排版版综述](output/pdf/金融文本预测_研究综述.pdf)：保留初轮420条检索的历史口径。','- [小模型补充阅读](docs/GPT2小模型补充阅读.md)。','- [完整引用库](catalog/references.bib)与[结构化题录](catalog/papers.json)。','- [离线交互文献库](index.html)：下载仓库后用浏览器打开；GitHub文件页本身显示源码，在线阅读用上面的中文目录。','', '## 按主题浏览','', '|分类|条数|','|---|---|']
for f,name in cats:readme.append(f'|[{name}](categories/{f}.md)|{counts[f]}|')
readme+=['', '每篇分配一个主分类，另保留多主题标签。通用时序、宏观、风险与交易决策论文分别标明用途，不冒充同一种个股收益预测证据。','', '## 质量与更新','', '- 原420条中的357条经过Crossref单DOI—题名匹配，63条依据仓储或数据库元数据。新增记录另保留原始来源核验。','- 代表集也不等于全部已复现：每篇公开核读层级，近期预印本和模拟蓝图不会被写成成熟共识。','- [自动覆盖与链接检查](catalog/repository_checks.json)；[初轮检索说明](literature_review/检索与核验说明.md)。','- 所有说明、导航与导读使用中文；英文原始文献信息保留便于准确核对。','', '论文PDF按各自许可原样提供并逐篇署名，不随本仓库说明文本统一重新授权。','']
(P/'README.md').write_text('\n'.join(readme))
status=['# 全文获取与公开状态','', '[返回首页](../README.md)','',f'共{len(xs)}条，公开保存PDF {npdf}份。全部条目均保留原文入口。个人可阅读与可公开转载是不同权限；未确认转载许可的PDF不出现在公开树中。','','|编号|中文导读或原文题名|公开状态|阅读|','|---|---|---|---|']
for x in xs:status.append(f'|{x["id"]}|[{label(x["id"])}](../papers/{x["id"]}.md)|{"可公开全文" if mf[x["id"]]["status"]=="pdf_downloaded" else "原文链接"}|{access(x)}|')
(P/'catalog/FULLTEXT_STATUS.md').write_text('\n'.join(status)+'\n')
lic=['# 公开全文与引用说明','', '[返回首页](../README.md)','', '只在明确的原文许可、PDF内许可或适用的来源政策支持下公开提供原样PDF。开放下载不自动等于允许在其他服务器重新托管。其余论文提供原始入口，不替换成来源不明的镜像。','', '每份公开PDF的作者、原始题名、原文、下载源、版本、许可与校验值见阅读卡及[逐篇许可记录](../catalog/public_pdf_licenses.json)。含非商业条件的许可用于本研究文献库；含禁止演绎条件的PDF原样保留。原论文权利不受本库笔记影响。','', '公开前的完整私有版本已在本地保留恢复存档；公开提交从经过许可检查的文件树建立，不将旧私有副本夹带在公开分支历史中。','', '|编号|论文|许可|来源证据|','|---|---|---|---|']
for x in xs:
 r=mf[x['id']]
 if r['status']=='pdf_downloaded':
  q=r['public_redistribution'];lic.append(f'|{x["id"]}|[{label(x["id"])}](../papers/{x["id"]}.md)|'+ '；'.join(f'[{u}]({u})' for u in q['license_urls'])+f'|[{q["evidence"]}]({q["evidence_url"]})|')
(P/'docs/公开全文与引用说明.md').write_text('\n'.join(lic)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
