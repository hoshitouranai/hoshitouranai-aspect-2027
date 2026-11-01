from bs4 import BeautifulSoup
from pathlib import Path
import re, hashlib, json
src=Path('/mnt/data/2027年1月_採用デザイン維持_統合解釈6件追加_DRAFT.html')
out=Path('/mnt/data/2027年1月_採用デザイン維持_全枠読み方ガイド追加_DRAFT.html')
soup=BeautifulSoup(src.read_text(encoding='utf-8'),'html.parser')
arts=soup.find_all('article'); counts={'existing':0,'specific':0,'pending':0}
for a in arts:
 if a.select_one('.guide'):
  counts['existing']+=1; continue
 h=a.find('h3',string='統合解釈'); p=h.find_next_sibling('p') if h else None
 if not p: continue
 actors=[x.find('b').get_text(' ',strip=True) for x in a.select('.actor') if x.find('b')]
 links=[x.get_text(' ',strip=True) for x in a.select('ul li')]
 description=p.get_text(' ',strip=True)
 pending=('保留' in description or '個別の統合審査が必要' in description or '未検証' in description)
 guide=soup.new_tag('div',attrs={'class':'guide'})
 strong=soup.new_tag('strong'); strong.string=('こう読むと分かりやすい｜読み方の手順（解釈保留）' if pending else 'こう読むと分かりやすい｜この配置の読み方'); guide.append(strong)
 para=soup.new_tag('p'); para.string='まず、'+'、'.join(actors)+'について、天体の働きと各サインでの表れ方を一体として読む。'; guide.append(para)
 para2=soup.new_tag('p'); para2.string='次に、'+('／'.join(links))+'。この関係が同じ時間帯に重なる点を見る。' if links else '次に、天体同士の関係を確認する。'; guide.append(para2)
 note=soup.new_tag('p',attrs={'class':'guide-note'})
 if pending:
  note.string=('この配置は'+('天体位置の検証が残っているため、具体的な結論はまだ導かない。' if '未検証' in description or '位置' in description else '各天体の役割と関係の統合審査が残っているため、結論を保留する。')+'読み方の手順のみを示している。')
  counts['pending']+=1
 else:
  note.string='以上を踏まえ、統合解釈にある「'+description[:85].rstrip('、。')+('…' if len(description)>85 else '')+'」という論点へ進む。これは占星術の象徴的な読み方であり、社会現象を断定するものではない。'
  counts['specific']+=1
 guide.append(note); p.insert_after(guide)
# compare css and existing guide verbatim using soup
orig=BeautifulSoup(src.read_text(encoding='utf-8'),'html.parser')
assert len(arts)==74
assert all(a.select_one('.guide') for a in arts)
assert str(orig.select_one('style'))==str(soup.select_one('style'))
assert str(orig.find('article').select_one('.guide'))==str(soup.find('article').select_one('.guide'))
assert [a.find('h3',string='統合解釈').find_next_sibling('p').get_text() for a in orig.find_all('article')]==[a.find('h3',string='統合解釈').find_next_sibling('p').get_text() for a in arts]
out.write_text(str(soup),encoding='utf-8')
print(json.dumps({'articles':len(arts), 'guides':len(soup.select('.guide')),'added':73,'counts':counts,'css_unchanged':True,'interpretations_unchanged':True,'file':str(out)},ensure_ascii=False,indent=2))
