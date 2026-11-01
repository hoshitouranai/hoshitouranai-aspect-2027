import csv,re,html,hashlib,json,os
from pathlib import Path
from bs4 import BeautifulSoup
base=Path('/mnt/data')
source=base/'2027年1月_日付_天体_サイン_アスペクト_プルダウン検索.html'
rowsfile=base/'aspect_triple_interpretation_v2_DRAFT/2027_3天体_天体サイン関係_統合草案666.csv'
out=base/'2027年_年間3天体アスペクト_日付自由入力_検索版_DRAFT.html'
soup=BeautifulSoup(source.read_text(encoding='utf-8'),'html.parser')
jan_cards=soup.select('section > article'); assert len(jan_cards)==74
with rowsfile.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==666
existing={c.select_one('header span').get_text(' ',strip=True).split('／')[-1].strip():str(c) for c in jan_cards}
assert len(existing)==74
signmean={'牡羊':'自ら先に動き、新しい方向を切り開く','牡牛':'継続性や手応えを大切にして定着させる','双子':'情報を交換し複数の視点を行き来する','蟹':'身近な集団や生活の安心を守る','獅子':'創造性や自己表現を前面に出す','乙女':'細部の検証と改善を積み重ねる','天秤':'他者との交渉や均衡を図る','蠍':'深い関与と共有資源に向き合う','射手':'理念や探究、遠い視野を広げる','山羊':'構造化し長期的責任を引き受ける','水瓶':'集団や技術、改革の仕組みを通じる','魚':'共感や想像、境界のあいまいさに関わる'}
planetmean={'太陽':'方向性や中心的意思','月':'生活感覚や人々の反応','水星':'情報の伝達や交渉','金星':'価値・関係・交換','火星':'行動や競争、推進','木星':'発展や拡大','土星':'責任や制度、制約','天王星':'刷新や変化','海王星':'理想やイメージ、曖昧さ','冥王星':'根底からの変容や権力構造','ドラゴンヘッド':'社会的な結び付きや方向付け','キロン':'傷や回復をめぐる象徴'}
aspectmean={'合':'働きが一体になる','セクスタイル':'相互に活用できる可能性が生じる','スクエア':'摩擦や調整課題が現れる','トライン':'働きが連携しやすい','インコンジャンクト':'異なる前提のすり合わせが必要になる','オポジション':'対峙や役割の分担が表に出る'}
H=lambda x:html.escape(str(x),quote=True)
articles=[];months={}
for r in rows:
 id=r['ID']; date=r['開始JST'][:10]; m=int(date[5:7]);months[m]=months.get(m,0)+1
 if id in existing:
  articles.append(existing[id]);continue
 ps=[r['天体'+str(i)] for i in range(1,4)]
 signs=[r[f'天体{i}_同時刻サイン'] for i in range(1,4)]
 pos=[r[f'天体{i}_同時刻位置'] for i in range(1,4)]
 aspects=[r['1-2アスペクト'],r['1-3アスペクト'],r['2-3アスペクト']]
 cards=[]
 for p,s,position in zip(ps,signs,pos):
  meaning=planetmean.get(p,'象徴的な働き')
  if s in signmean and r.get(f'天体{ps.index(p)+1}_計算状態')=='計算済':
   body=f'{H(p)}は「{H(meaning)}」を象徴する天体。{H(s)}座では「{H(signmean[s])}」ような形でその働きが現れると読む。'
  else:body='この天体の同時刻位置は未検証のため、サインを含む解釈は保留。'
  cards.append(f'<div class="actor"><b>{H(p)}｜{H(position or "—")}</b><p>{body}</p></div>')
 pair_indices=[(0,1),(0,2),(1,2)]
 rel=''.join(f'<li>{H(ps[i])}と{H(ps[j])}の{H(a)}：{H(aspectmean.get(a,"象徴的な関係"))}。</li>' for (i,j),a in zip(pair_indices,aspects))
 note='同時刻の天体位置が未検証のため、統合解釈は保留。' if r['中点_三辺同時オーブ内']!='PASS' else '各天体の働きと3つの関係を照合するための資料。配置固有の社会的統合解釈は内容審査待ち。'
 start=r['開始JST'][:10];end=r['終了JST'][:10]
 signs_v='|'.join(s+'座' for s in signs if s)
 articles.append(f'<article data-start="{H(start)}" data-end="{H(end)}" data-planets="{H("|".join(ps))}" data-signs="{H(signs_v)}" data-aspects="{H("|".join(aspects))}"><header><b>{H(r["開始JST"])} ～ {H(r["終了JST"])}</b><span>{H(r["形状分類"])} ／ {H(id)}</span></header><div class="people">{"".join(cards)}</div><h3>3天体の関係</h3><ul>{rel}</ul><h3>統合解釈</h3><p>{H(note)}</p><small>占星術的な解釈草案。独立天文照合・意味審査は未完了。 同時刻オーブ検査：{H(r["中点_三辺同時オーブ内"])}</small></article>')
# transplant styles and header (January original CSS), preserving approved colors/layout
style=str(soup.style)
# use original guide intro, avoid new content in explanatory header
intro=str(soup.select_one('.guide-intro'))
planetopts=['太陽','月','水星','金星','火星','木星','土星','天王星','海王星','冥王星','ドラゴンヘッド','キロン']
signopts=[x+'座' for x in signmean]
aspopts=['合','セクスタイル','スクエア','トライン','インコンジャンクト','オポジション']
def opts(values,name):return '<option value="">'+name+'</option>'+''.join(f'<option value="{H(x)}">{H(x)}</option>' for x in values)
controls='''<div class="filters"><label class="filter-field"><span class="filter-label">日付（自由入力）</span><input id="dateQuery" type="text" inputmode="text" placeholder="例：1/1、1月1日、2027-01-01" autocomplete="off" /></label>'''+''.join('<label class="filter-field"><span class="filter-label">'+label+'</span><select id="'+name+'">'+opts(values,'すべての'+label)+'</select></label>' for name,label,values in [('planet','天体',planetopts),('sign','サイン',signopts),('aspect','アスペクト',aspopts)])+'''<div class="filter-field"><span class="filter-label">検索解除</span><button id="resetFilters" type="button">すべて解除</button></div></div><p class="search-count" id="searchCount" aria-live="polite"></p>'''
js=r'''(()=>{'use strict';
const cards=Array.from(document.querySelectorAll('#results > article'));
const q=document.getElementById('dateQuery'),p=document.getElementById('planet'),s=document.getElementById('sign'),a=document.getElementById('aspect'),counter=document.getElementById('searchCount');
function parseDate(raw){
 let t=raw.trim().replace(/\s/g,'').replace(/[０-９]/g,c=>String.fromCharCode(c.charCodeAt(0)-65248)).replace(/[／]/g,'/').replace(/[－ー]/g,'-');
 if(!t)return {date:'',error:''};
 let y=2027,m,d,match;
 if((match=t.match(/^(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?$/))){y=+match[1];m=+match[2];d=+match[3];}
 else if((match=t.match(/^(\d{1,2})月(\d{1,2})日?$/))){m=+match[1];d=+match[2];}
 else if((match=t.match(/^(\d{1,2})[/-](\d{1,2})$/))){m=+match[1];d=+match[2];}
 else return {date:'',error:'日付は「1/1」「1月1日」「2027-01-01」の形式で入力してください。'};
 const dt=new Date(Date.UTC(y,m-1,d));
 if(y!==2027||dt.getUTCFullYear()!==y||dt.getUTCMonth()+1!==m||dt.getUTCDate()!==d)return {date:'',error:'2027年の正しい日付を入力してください。'};
 return {date:`${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`,error:''};
}
function has(str,v){return !v||(str||'').split('|').includes(v);}
function update(){
 const v=parseDate(q.value), date=v.date;let n=0;
 for(const card of cards){let ok=!v.error&&(!date||card.dataset.start<=date&&date<=card.dataset.end)&&has(card.dataset.planets,p.value)&&has(card.dataset.signs,s.value)&&has(card.dataset.aspects,a.value);
 card.hidden=!ok;card.style.display=ok?'':'none';if(ok)n++;}
 counter.textContent=v.error||`該当 ${n}件／全 ${cards.length}件`+(n===0?'　条件に一致する配置がありません。':'');
}
q.addEventListener('input',update);[p,s,a].forEach(c=>c.addEventListener('change',update));document.getElementById('resetFilters').addEventListener('click',()=>{q.value='';[p,s,a].forEach(x=>x.value='');update()});update();
})();'''
js=js.replace('\\\\','\\')
page='<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2027年｜3天体アスペクト統合分析</title>'+style+'<style>.filters input{width:100%;margin:0;box-sizing:border-box}.filters{grid-template-columns:repeat(auto-fit,minmax(165px,1fr))}article[hidden]{display:none!important}</style></head><body><h1>2027年｜天体・サイン・関係の読み解き</h1>'+intro+controls+'<section id="results">'+''.join(articles)+'</section><script>'+js+'</script></body></html>'
out.write_text(page,encoding='utf-8')
# basic verifications
s=BeautifulSoup(page,'html.parser'); cards=s.select('#results > article');assert len(cards)==666
assert len([x for x in cards if x.select_one('header span').get_text().strip().endswith('T0001')])==1
assert all(len(x['data-start'])==10 and len(x['data-end'])==10 for x in cards)
print(out, 'bytes',out.stat().st_size,'cards',len(cards),'january_preserved',len(existing),'months',months,'sha256',hashlib.sha256(out.read_bytes()).hexdigest())
