import csv, pathlib, json, hashlib, html, zipfile
from collections import Counter
src=pathlib.Path('/mnt/data/aspect_triple_midpoint_DRAFT/2027_三天体_中点同時刻サイン_666件_DRAFT.csv')
out=pathlib.Path('/mnt/data/aspect_triple_interpretation_v2_DRAFT');out.mkdir(exist_ok=True)
with src.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
planets={'太陽':'方向性・中心的意思','月':'生活感覚・日常的な反応','水星':'情報・伝達・交渉','金星':'価値観・関係調整','火星':'行動・対立・推進','木星':'拡大・展望','土星':'責任・制約・制度','天王星':'変革・技術的刷新','海王星':'理想・境界の曖昧さ','冥王星':'権力構造・根本的転換','ドラゴンヘッド':'集団的方向・つながり','キロン':'傷つきやすさ・修復という象徴'}
signs={'牡羊':'先行・自発的な着手','牡牛':'資源・保持・安定','双子':'複数の情報・接続','蟹':'暮らし・保護・帰属','獅子':'表現・中心性・創造','乙女':'実務・検証・改善','天秤':'対等な関係・調整','蠍':'共有資源・深い変化','射手':'探求・展望・理念','山羊':'構造化・長期的責任','水瓶':'共同体・制度刷新','魚':'共感・境界を越える連帯'}
act={'合':'結び付く','セクスタイル':'選択的に協力する','スクエア':'摩擦や調整を生む','トライン':'協調しやすい','インコンジャンクト':'異なる前提を調整する','オポジション':'向き合い緊張関係になる','衝':'向き合い緊張関係になる','六分':'選択的に協力する','三分':'協調しやすい'}
def planet_sign(n,s):return f'{n}は「{planets.get(n,"固有の天体象徴")}」を、{s}座の「{signs.get(s,"サイン固有の性質")}」という形で働かせる'
def make(r):
 ns=[r[f'天体{i}'] for i in (1,2,3)]; ss=[r[f'天体{i}_同時刻サイン'] for i in (1,2,3)]
 pairs=[(0,1,r['1-2アスペクト']),(0,2,r['1-3アスペクト']),(1,2,r['2-3アスペクト'])]
 core=[planet_sign(n,s) if s in signs else f'{n}：同時刻サイン未検証' for n,s in zip(ns,ss)]
 conjunction=[(a,b) for a,b,asp in pairs if asp=='合']; opposition=[(a,b) for a,b,asp in pairs if asp in ('オポジション','衝')]
 stress=[(a,b) for a,b,asp in pairs if asp=='スクエア']
 hub=None
 if conjunction:
  a,b=conjunction[0]; c=next(i for i in range(3) if i not in (a,b)); aspA=next((asp for x,y,asp in pairs if set((x,y))==set((a,c))), '?');aspB=next((asp for x,y,asp in pairs if set((x,y))==set((b,c))), '?')
  structural=f'{ns[a]}と{ns[b]}の働きが合で結び付く。そのまとまりに{ns[c]}が{aspA}と{aspB}で関わるため、単独の天体同士ではなく「結び付いた二つの働きと、第三の働きとの関係」として読む。'
  direction=f'{ns[a]}の「{planets.get(ns[a],"固有の性質")}」と{ns[b]}の「{planets.get(ns[b],"固有の性質")}」が、{ns[c]}の「{planets.get(ns[c],"固有の性質")}」とどのように両立・調整されるかが中心の論点。'
 elif len(stress)>=2:
  ct=Counter(i for a,b in stress for i in (a,b));hub=ct.most_common(1)[0][0]
  other=[i for i in range(3) if i !=hub]
  rel=next((asp for a,b,asp in pairs if set((a,b))==set(other)),'不明')
  structural=f'{ns[hub]}が{ns[other[0]]}と{ns[other[1]]}の双方にスクエアを形成する。残る二天体は{rel}でつながるため、{ns[hub]}の働きが全体の調整点になる。'
  direction=f'{ns[hub]}の「{planets.get(ns[hub],"固有の性質")}」が、ほかの二天体の働きにどのような調整圧力を与えるかを検討する。'
 elif opposition:
  a,b=opposition[0];c=next(i for i in range(3) if i not in (a,b))
  structural=f'{ns[a]}と{ns[b]}の対向関係を軸とし、{ns[c]}が双方との関係によって緊張を強めるか、調整の経路を作るかを読む。'
  direction=f'対立する「{planets.get(ns[a],"")}」と「{planets.get(ns[b],"")}」の間で「{planets.get(ns[c],"")}」が果たす役割を検討する。'
 else:
  structural='三つのアスペクトを独立した意味の足し算として扱わず、三天体の働きが同時にどう結び付くかを読む。'
  direction='協調・摩擦・調整の関係がどの天体間にあるかを比較し、中心となる働きと制約を特定する。'
 known=all(s in signs for s in ss) and all(r[f'天体{i}_計算状態']=='計算済' for i in (1,2,3))
 state='天体位置あり・内容審査待ち' if known else '天体位置未検証・解釈保留'
 if not known:structural='同時刻の天体位置が一部不足しているため、構造のみ記録し、サイン統合解釈は保留する。';direction='位置データを補完してから解釈する。'
 return core,structural,direction,state
for r in rows:
 c,s,d,state=make(r)
 r['天体サインの働き_統合前提']=' ／ '.join(c)
 r['三天体の関係構造_新規']=s
 r['統合解釈の中心論点_新規']=d
 r['新規解釈の審査状態']=state
 r['注意書き']='占星術的象徴の検討用草案。具体的な出来事の予測ではない。';r['比喩の扱い']='解説メモのみ・プログラム出力には不使用'
cols=list(rows[0]);dest=out/'2027_3天体_天体サイン関係_統合草案666.csv'
with dest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
jan=[r for r in rows if r['開始JST'].startswith('2027-01')]
style='''body{font-family:system-ui,-apple-system,sans-serif;max-width:1100px;margin:30px auto;padding:0 16px;color:#17243c;background:#f6f8fb}h1{font-size:24px} .note{background:#fff5df;padding:12px;border-radius:8px}.item{background:white;border:1px solid #d9e0ea;border-radius:12px;padding:17px;margin:12px 0}.muted{color:#596a80;font-size:13px}.k{font-weight:700;color:#254f7c;margin-top:12px}.details{margin-top:12px}summary{cursor:pointer;color:#254f7c}input{width:100%;padding:12px;font-size:16px;border-radius:8px;border:1px solid #ccd}'''
parts=[f'<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>2027年1月 三天体の統合解釈</title><style>{style}</style><h1>2027年1月｜天体×サイン×三天体の関係</h1><p class="note">計算済みの天体位置に基づく占星術的解釈の草案です。未審査・未検証は明示。人への比喩は独立メモにのみ保存し、この分析には表示しません。</p><input id="q" placeholder="天体名・サイン・アスペクト・キーワードで検索" oninput="filter()">']
for r in jan:
 esc=lambda t:html.escape(str(t))
 title='・'.join(f'{r[f"天体{i}"]}（{r[f"天体{i}_同時刻位置"] or "位置未確認"}）' for i in (1,2,3))
 blob=' '.join(str(v) for v in r.values())
 parts.append(f'<article class="item" data-search="{esc(blob)}"><div><b>{esc(title)}</b></div><p class="muted">{esc(r["開始JST"])} ～ {esc(r["終了JST"])}｜ {esc(r["形状分類"])}｜{esc(r["新規解釈の審査状態"])}</p><div class="k">それぞれの天体がサインでどう働くか</div><p>{esc(r["天体サインの働き_統合前提"])}</p><div class="k">三天体の関係</div><p>{esc(r["三天体の関係構造_新規"])}</p><div class="k">統合解釈の中心論点</div><p>{esc(r["統合解釈の中心論点_新規"])}</p><details class="details"><summary>計算条件・アスペクトを確認</summary><p>{esc(r["1-2アスペクト"])}・{esc(r["1-3アスペクト"])}・{esc(r["2-3アスペクト"])}／評価：{esc(r["同時評価時刻JST"])}／オーブ：{esc(r["中点_三辺オーブ°"])}／{esc(r["中点_三辺同時オーブ内"])}</p></details></article>')
parts.append('''<script>function filter(){const q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('.item').forEach(e=>e.style.display=e.dataset.search.toLowerCase().includes(q)?'':'none')}</script></html>''')
htmlpath=out/'2027年1月_天体サイン統合解釈_74件.html';htmlpath.write_text('\n'.join(parts),encoding='utf-8')
summary={'total':len(rows),'january':len(jan),'verified_position':sum(r['新規解釈の審査状態'].startswith('天体位置あり') for r in rows),'position_missing':sum(r['新規解釈の審査状態'].startswith('天体位置未検証') for r in rows),'full_meaning_review_pass':0,'three_body_html':str(htmlpath.name),'original_preserved':True}
(out/'検査レポート.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'README.txt').write_text('天体の働き→サインによる働き方→三天体の関係構造→統合の論点を自動生成するDRAFT。人物比喩は出力しない。内容は未承認。独立天文照合未完了。再生成: python build_integrated_triple_v2.py（入力パスは環境に合わせて配置）。',encoding='utf-8')
zipname=pathlib.Path('/mnt/data/工程15_天体サイン関係_統合解釈_改訂DRAFT.zip')
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED) as z:
 for p in out.iterdir():z.write(p,p.name)
 z.write(__file__,'build_integrated_triple_v2.py')
print(json.dumps(summary,ensure_ascii=False));print(htmlpath,zipname)
