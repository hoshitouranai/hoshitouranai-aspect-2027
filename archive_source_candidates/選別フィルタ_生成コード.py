from bs4 import BeautifulSoup
from pathlib import Path
import re, json
src=Path('/mnt/data/2027年1月_日付検索_動作修正版.html')
out=Path('/mnt/data/2027年1月_日付_天体_サイン_アスペクト_プルダウン検索.html')
soup=BeautifulSoup(src.read_text(encoding='utf-8'),'html.parser')
articles=soup.select('section > article')
assert len(articles)==74
planets=['太陽','月','水星','金星','火星','木星','土星','天王星','海王星','冥王星','ドラゴンヘッド','キロン']
signs=['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座']
existing=soup.select_one('.filters'); assert existing
existing.clear()

def select(id, label, options):
    wrap=soup.new_tag('label', **{'class':'filter-field'})
    title=soup.new_tag('span', **{'class':'filter-label'});title.string=label
    sel=soup.new_tag('select',id=id)
    for value, display in options:
        opt=soup.new_tag('option',value=value);opt.string=display;sel.append(opt)
    wrap.append(title);wrap.append(sel);existing.append(wrap)
select('day','日付',[('', 'すべての日付')]+[(str(i),f'1月{i}日') for i in range(1,32)])
select('planet','天体',[('','すべての天体')]+[(p,p) for p in planets])
select('sign','サイン',[('','すべてのサイン')]+[(s,s) for s in signs])
select('aspect','アスペクト',[('','すべてのアスペクト')]+[(n,n) for n in ['合','セクスタイル','スクエア','トライン','インコンジャンクト','オポジション']])
reset=soup.new_tag('button',id='resetFilters',type='button');reset.string='絞り込みを解除';existing.append(reset)
count=soup.new_tag('p',id='searchCount',**{'class':'search-count'});existing.insert_after(count)
# attach normalized metadata for exact matching, separate roles (planet and sign anywhere in same configuration)
for art in articles:
    names=[]; signs_in=[]
    for actor in art.select('.actor b'):
        txt=actor.get_text(' ',strip=True)
        for p in planets:
            if txt.startswith(p+'｜'):
                names.append(p);break
        for s in signs:
            if s in txt:signs_in.append(s);break
    lines=[li.get_text(' ',strip=True) for li in art.select('ul li')]
    aspects=[]
    for line in lines:
        if 'の' not in line:continue
        for a in ['インコンジャンクト','オポジション','セクスタイル','スクエア','トライン','合']:
            if 'の'+a in line:aspects.append(a);break
    art['data-planets']='|'.join(names)
    art['data-signs']='|'.join(signs_in)
    art['data-aspects']='|'.join(aspects)
    assert names and aspects
for sc in soup.select('script'):sc.decompose()
script=r'''(()=>{
'use strict';
const cards=[...document.querySelectorAll('section > article')];
const ids=['day','planet','sign','aspect'];
const controls=Object.fromEntries(ids.map(k=>[k,document.getElementById(k)]));
const counter=document.getElementById('searchCount');
function contains(field,value){return !value||field.split('|').includes(value);}
function update(){
 const d=controls.day.value,p=controls.planet.value,s=controls.sign.value,a=controls.aspect.value;
 const date=d?`2027-01-${d.padStart(2,'0')}`:'';
 let n=0;
 for(const card of cards){
  const ok=(!date||(card.dataset.start<=date&&date<=card.dataset.end))&&contains(card.dataset.planets||'',p)&&contains(card.dataset.signs||'',s)&&contains(card.dataset.aspects||'',a);
  card.hidden=!ok;
  card.style.display=ok?'':'none';
  if(ok)n++;
 }
 counter.textContent=`該当 ${n}件／全${cards.length}件`+(n===0?'　選択条件を変えてみてください。':'');
}
ids.forEach(k=>controls[k].addEventListener('change',update));
document.getElementById('resetFilters').addEventListener('click',()=>{ids.forEach(k=>controls[k].value='');update();});
update();
})();'''
sc=soup.new_tag('script');sc.string=script;soup.body.append(sc) if soup.body else soup.append(sc)
style=soup.select_one('style');style.string += '''\n.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0;align-items:end}.filter-field{display:flex;flex-direction:column;gap:5px}.filter-label{font-size:.9rem;font-weight:650}.filters select{width:100%;margin:0;box-sizing:border-box}.filters button{font:inherit;background:#fff;border:1px solid #becba9;color:#37432f;border-radius:8px;padding:10px;cursor:pointer}.search-count{color:#48583e;font-weight:600;margin:6px 0 16px}'''
out.write_text(str(soup),encoding='utf-8')
# static independent evaluation of test cases (same predicate as JS)
def test(day='',planet='',sign='',aspect=''):
 date=f'2027-01-{int(day):02}' if day else ''
 res=[a for a in articles if (not date or a['data-start']<=date<=a['data-end']) and (not planet or planet in a['data-planets'].split('|')) and (not sign or sign in a['data-signs'].split('|')) and (not aspect or aspect in a['data-aspects'].split('|'))]
 return len(res)
cases={'全件':test(),'1月1日':test(day='1'),'土星':test(planet='土星'),'スクエア':test(aspect='スクエア'),'山羊座':test(sign='山羊座'),'1月1日＋土星＋スクエア':test(day='1',planet='土星',aspect='スクエア')}
assert cases['全件']==74 and cases['1月1日']>0 and cases['土星']>0 and cases['スクエア']>0
print(out, out.stat().st_size, json.dumps(cases,ensure_ascii=False))
