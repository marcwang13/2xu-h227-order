# 一次性：把 DSTC 範本 index.html（先複製成 index.html.dstc_base）改成 2XU 版 index.html。之後 DSTC 範本有新功能要同步時，可重新複製 base 再跑一次，逐條核對失敗的取代。
import re,sys
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
s=open(R+'index.html.dstc_base').read()
def rep(a,b,cnt=None,regex=False):
    global s
    n=len(re.findall(a,s)) if regex else s.count(a)
    if n==0 or (cnt is not None and n!=cnt):
        print('!! count',n,'for',a[:90]); sys.exit(1)
    s=re.sub(a,b,s) if regex else s.replace(a,b)
def cut(start,end,new=''):
    global s
    i=s.index(start); j=s.index(end,i)+len(end); s=s[:i]+new+s[j:]

# --- 標題、品牌、色系 ---
rep('<title>DESCENTE 27FW 正式訂貨（27Q3Q4）</title>','<title>2XU H2-27 正式訂貨</title>',1)
rep('/* DSTC filter: four levels, four shapes */','/* 2XU：沿用 DSTC 篩選版面 */',1)
rep('--acc:#0b57c2; --acc-ink:#ffffff; --acc-soft:#e1ecfb;','--acc:#1a1a1a; --acc-ink:#ffffff; --acc-soft:#ececec;',1)
rep('--brand:#0a3f94; --brand-ink:#ffffff; --brand-2:#072d6c;','--brand:#111111; --brand-ink:#ffffff; --brand-2:#000000;',1)
rep('--acc:#6aa5f5; --acc-ink:#0b1019; --acc-soft:#16294a;','--acc:#e6e6e6; --acc-ink:#111111; --acc-soft:#2a2a2a;',2)
rep('--brand:#14408c; --brand-ink:#ffffff; --brand-2:#0c2b61;','--brand:#1c1c1c; --brand-ink:#ffffff; --brand-2:#000000;',2)
rep(':root{--heat:#0b57c2;--btn-pri:#0b57c2;--btn-sec-bg:#eef4fd;--btn-sec-bd:#0b57c2;--btn-sec-fg:#0b57c2}',':root{--heat:#333333;--btn-pri:#111111;--btn-sec-bg:#f2f2f2;--btn-sec-bd:#111111;--btn-sec-fg:#111111}',1)
rep('--heat:#3f7fd9;--btn-pri:#1f5bb5;--btn-sec-bg:#16294a;--btn-sec-bd:#3f7fd9;--btn-sec-fg:#cfe0fb','--heat:#9a9a9a;--btn-pri:#3a3a3a;--btn-sec-bg:#2a2a2a;--btn-sec-bd:#9a9a9a;--btn-sec-fg:#eeeeee',2)
rep("const OV_COL=['#0a3f94','#3f7fd9','#8fb8ee','#c9dcf6',","const OV_COL=['#111111','#555555','#8a8a8a','#c4c4c4',",1)
rep('#0a3f94','#111111'); rep('FF0A3F94','FF111111')
rep('<img class="whl-logo" src="https://emerswhl-restock.surge.sh/brand/logo-full.png" alt="EMERS-WHL TW"><span class="whl-sep" aria-hidden="true"></span><b>DESCENTE</b><span>27FW 正式訂貨</span>',
    '<img class="whl-logo" src="logo.png" alt="EMERS-WHL TW"><span class="whl-sep" aria-hidden="true"></span><b>2XU</b><span>H2-27 正式訂貨</span>',1)
rep('DESCENTE 業務','2XU 業務')

# --- 移除過往參考 UI ---
cut('    <div class="dnote" id="refnote">','</details></div>\n')
cut('      <div class="lv lv-rg">','</div></div>\n')
cut('        <label class="toggle"><input type="checkbox" id="hotsort">','</label>\n')
rep("$('#hotsort').addEventListener('change',e=>{ S.hot=e.target.checked; renderList(); toListTop(); });\n",'',1)
rep('<div class="stat" hidden><small>韓幣金額</small>','<div class="stat"><small>零售金額 NT$</small>',1)

# --- 字串、key、前綴 ---
rep('dstc-27fw-','2xu-h227-')
rep("'dstc-admin',","'dstc-admin','2xu-admin',",1)
rep("'dstc-","'2xu-")
rep('DSTC27-','2XU27-')
rep('DESCENTE 27FW 27Q3Q4','2XU H2-27'); rep('DESCENTE_27Q3Q4','2XU_H2-27'); rep('DESCENTE 27Q3Q4','2XU H2-27')
rep('韓幣 MSRP(₩)','建議售價(NT$)'); rep('韓幣金額(₩)','零售金額(NT$)')
rep('金額暫以韓幣 MSRP（₩）計，台灣定價待定','金額以台灣建議售價（NT$ MSRP）計',1)
rep("wb.creator='2XU H2-27'","wb.creator='2XU H2-27'")
rep('｜台灣定價待定、尺寸參考前季等「資料待更新說明」見「總表」G 欄。','｜下單截止日、商品說明等「資料待更新說明」見「總表」G 欄。',1)
rep('｜尺寸待原廠更新，目前參考之前的尺寸。','',1)

# --- 資料檔 ---
rep('<script src="pc.js?v=20261118d"></script>\n','',1)
rep('<script src="ref.js?v=20261119u"></script>\n','',1)
rep('config.js?v=20261118c','config.js?v=20261123a',1)
rep('data.js?v=20261118c','data.js?v=20261123a',1); rep('imgs.js?v=20261118e','imgs.js?v=20261123a',1); rep('rp.js?v=20261120a','rp.js?v=20261123a',1)
rep('window.DSTC_','window.X2_'); rep('DSTC_REF.s','X2_REF.s')
rep('// 實體圖（rp.js）：DSTC_RPI','// 實體圖（rp.js）：X2_RPI',1)
rep('// 同款借圖（rp.js DSTC_RPB）','// 同款借圖（rp.js X2_RPB）',1)
rep('const big = h=>`big/${h}.jpg`;','const big = h=>`big/${h}.jpg`;\n// 款式圖借同款（原廠訂單表沒附這色的圖）：說明放進備註，卡片與 Excel 都看得到\nITEMS.forEach(i=>{ if(i.dollBorrow) i.note=[i.note,i.dollBorrow].filter(Boolean).join(\'\\n\'); });\nconst ttl=it=>esc(it.en||it.zh), sub2=it=>esc(it.zh||\'\');\nconst whenOf=it=>it.drop||\'\';  // 只顯示 Drop 1／2／3，不換算月份',1)

# --- 資料待更新說明 ---
i=s.index('function dataNotes(web){'); j=s.index('\n}\n',i)+3
s=s[:i]+r'''function dataNotes(web){
  const nRP=ITEMS.filter(i=>i.hasRP).length, nRB=ITEMS.filter(i=>i.rpBorrow).length, nDB=ITEMS.filter(i=>i.dollBorrow).length;
  const nSt=new Set(ITEMS.map(i=>i.style)).size, nOv=new Set(ITEMS.filter(i=>i.ov||i.dt).map(i=>i.style)).size, nTall=ITEMS.filter(i=>i.sizes.some(z=>/T$/.test(z))).length;
  const L=['下單截止：2026/11/26（四）',
    '價格：顯示台灣建議售價（NT$ MSRP），金額＝建議售價 × 件數',
    `商品說明：${nOv}／${nSt} 款附原廠型錄英文說明（點「看商品細節與材質」），中文說明待補`,
    `款式圖：原廠訂單表附圖${nDB?`；其中 ${nDB} 款色原廠沒附自己顏色的圖，借同款其他顏色（標「同款參考／顏色不同」）`:''}`,
    `實體圖：${nRP} 款色有原廠型錄照片（點「實體圖」）${nRB?`；另 ${nRB} 款色借同款其他顏色的型錄照（標「同款實體圖」，顏色不同僅供款式參考）`:''}；型錄 PDF 已壓縮，照片解析度有限`,
    `尺寸：依原廠訂單表各色開放尺寸${nTall?`；${nTall} 款色另有加長版（XST／ST／MT／LT／XLT／XXLT，T＝Tall），排在一般尺寸後面`:''}`];
  return L;
}
'''+s[j:]

# --- 分頁、大類 ---
rep("const SHEETS = ['NEO-ARCHIVE','TRAINING','RUNNING','INSPIRED','SNOW','WOMENS SNOW','PREMIUM TECH ESSENTIAL','WOMENS','ACC 配件','FTW RUNNING','FTW MOVEWEAR'];",
    "const SHEETS = ['Aero','Light Speed','Aero Trail','X Core','Form','Force','Ignition','Signature','Recovery','Vectr','Fluid','Basics','Propel'];",1)
rep("const TAB_ORDER = ['TRAINING','RUNNING','INSPIRED','SNOW','WOMENS SNOW','PREMIUM TECH ESSENTIAL','WOMENS','ACC 配件','NEO-ARCHIVE','FTW RUNNING','FTW MOVEWEAR'];","const TAB_ORDER = SHEETS.slice();",1)
rep("const MONTH_ORDER = ['5月','6月','7月','8月','9月','10月','11月','12月'];","const MONTH_ORDER = ['Drop 1','Drop 2','Drop 3'];",1)
rep("const CG_ORDER=['上身','下身','配件','鞋類'];","const CG_ORDER=['上身','下身','配件'];",1)
rep("let S = {sheet:'TRAINING',","let S = {sheet:'Aero',",1)

# --- 卡片 ---
T1="<h3>${esc(it.zh||it.en)}</h3><span class=\"en\">${esc(it.en)}</span>"
rep(T1,"<h3>${ttl(it)}</h3><span class=\"en\">${sub2(it)}</span>",2)
rep("${it.icon?`<span class=\"tag\">${esc(it.icon)}</span>`:''}${it.eb?`<span class=\"tag eb\">${esc(ebLabel(it.eb))}</span>`:''}${refBadge(it)}${refColorHTML(it)}</div>",
    "${it.season==='新款'?'<span class=\"tag eb\">新款</span>':'<span class=\"tag\">延續款</span>'}${it.act?`<span class=\"tag\">${esc(it.act)}</span>`:''}${whenOf(it)?`<span class=\"tag\">${esc(whenOf(it))}</span>`:''}</div>",1)
rep("<div class=\"price\"><small>台灣定價待定</small></div>","<div class=\"price\"><small>建議售價</small>NT$${fmt(it.price)}</div>",1)
rep("<div class=\"share\">尺寸待更新（目前參考前季）${(it.photos||[]).length?'':'・實體圖待更新'}</div>","",1)
rep("${sh?(sh.ref?`<div class=\"share\">格子下方 %＝${esc(sh.k)}尺寸銷售佔比</div>`:`<div class=\"share\">上季 尺寸銷售佔比參考・<b>${esc(sh.k)}</b>${it.cat===\"短褲\"?\"（依長褲腰圍）\":\"\"}</div>`):\"\"}","",1)
rep("${it.theme&&it.theme!=='CORE'?' ／ '+esc(it.theme)+(it.drop?' '+esc(it.drop):''):''}・台灣定價待定・尺寸待更新（目前參考前季）${its.some(x=>!(x.photos||[]).length)?'・實體圖待更新':''}${refShare(it)?`・尺寸格下方 %＝${esc(refShare(it).k)}尺寸銷售佔比`:''}",
    "・${esc(it.sheet)}・${esc(it.act||'')}${whenOf(it)&&new Set(its.map(whenOf)).size===1?'・'+esc(whenOf(it)):''}",1)
rep("${it.icon?`<span class=\"tag\">${esc(it.icon)}</span>`:''}${refBadge(it)}</div>","</div>",1)
rep("<div class=\"meta\"><span class=\"tag c\">${esc(it.cc||'')}</span>${refColorHTML(it)}${it.eb?`<span class=\"tag eb\">${esc(ebLabel(it.eb))}</span>`:''}</div>",
    "<div class=\"meta\"><span class=\"tag c\">${esc(it.cc||'')}</span>${it.season==='新款'?'<span class=\"tag eb\">新款</span>':'<span class=\"tag\">延續款</span>'}${whenOf(it)&&new Set(ITEMS.filter(x=>x.style===it.style).map(whenOf)).size>1?`<span class=\"tag\">${esc(whenOf(it))}</span>`:''}</div>",1)
rep("<div class=\"ordtop\"><div class=\"sub\" data-sub>${subHTML(it)}</div></div>","<div class=\"ordtop\"><div class=\"price\"><small>建議售價</small>NT$${fmt(it.price)}</div><div class=\"sub\" data-sub>${subHTML(it)}</div></div>",1)
# 加長版（T）前面斷行
rep("(it.run==='U'?/(<label class=\"sz[^\"]*\"><span>M<small)/:/(?!)/)","/(<label class=\"sz[^\"]*\"><span>(?:XST|ST|MT|LT|XLT|XXLT)<\\/span>)/",2)
rep("const hay=[i.zh,i.en,i.ko,i.style,i.sku,i.color,i.cc,i.cat,i.theme]","const hay=[i.zh,i.en,i.style,i.sku,i.color,i.cc,i.cat,i.act,i.sheet,i.drop]",1)

# --- 系列介紹 ---
i=s.index('const SHEET_INTRO={'); j=s.index('const SXV=',i)
s=s[:i]+r'''const SHEET_INTRO={
 'Aero':{t:'跑步主力系列，輕量透氣布料。上衣、背心、短褲、外套到帽款、遮陽帽、袖套與跑步配件一次到位，H2-27 約一半是新款。',k:'Aero 短褲（5／7 吋、2-in-1、Hi-Rise）、Aero 背心與 Crop Tank、Aero 帽款與遮陽帽'},
 'Light Speed':{t:'競速跑步系列，以 2XU 壓縮布做比賽與高強度訓練用的壓縮緊身褲、壓縮短褲，另有 Kinesis 壓縮款、運動內衣、背心與帽款。',k:'Light Speed 壓縮緊身褲／壓縮短褲、Kinesis 壓縮系列、Light Speed 帽款'},
 'Aero Trail':{t:'越野跑系列，H2-27 以新款為主：輕量 1/2 拉鍊上衣、長短袖、背心、越野短褲、外套，以及越野帽款與跑步腰包。',k:'Aero Trail 1/2 Zip、Aero Trail Jacket、Trail Cargo 7" 短褲'},
 'X Core':{t:'核心壓縮系列（Core Compression），PWX 壓縮布支撐肌肉、穩定姿勢，長短袖、無袖、壓縮短褲、緊身褲與小腿套，全部是延續款。',k:'Core Compression 長袖／短袖、Core Compression 緊身褲與短褲、壓縮小腿套'},
 'Form':{t:'女款訓練壓縮系列：Stash 高腰壓縮褲（4／6 吋短褲、3/4、7/8、長褲，有收納口袋）與 Racerback 中強度運動內衣。',k:'Form Stash Hi-Rise 壓縮褲、Form Racerback 運動內衣'},
 'Force':{t:'訓練系列：Force 壓縮短褲、壓縮緊身褲、壓縮袖套，搭配 Tencel 寬版上衣與背心。',k:'Force 壓縮緊身褲／短褲、Force Oversize Tencel Tee'},
 'Ignition':{t:'跑步保暖與入門壓縮款：Ignition 壓縮長袖、Shield 壓縮緊身褲、Grid 1/2 拉鍊連帽上衣。',k:'Ignition Shield 壓縮緊身褲、Ignition Grid 1/2 Zip Hoodie'},
 'Signature':{t:'運動休閒系列，2XU 品牌經典上衣、背心、長袖、短褲與帽款，日常穿搭用。',k:'Signature Tee、Signature Soft Jersey 系列、Signature Cap'},
 'Recovery':{t:'恢復系列：FIR 遠紅外線壓縮緊身褲、壓縮袖套、腿套與恢復襪，運動後恢復用。',k:'Recovery FIR 壓縮緊身褲、Refresh 恢復緊身褲、FIR 壓縮襪'},
 'Vectr':{t:'機能運動襪，依緩衝分 Ultralight／Light Cushion／Cushion，長度從隱形襪到全長，跑步與訓練都有。',k:'Vectr Light Cushion、Vectr Cushion 系列'},
 'Fluid':{t:'訓練用止滑襪（Grip Socks），單雙與 3 雙組。',k:'Performance Crew Grip Socks'},
 'Basics':{t:'基本配件：襪子 3 雙組、細髮帶 2 入、鐵人號碼帶、免綁鞋帶。',k:''},
 'Propel':{t:'游泳系列：Propel 泳鏡。',k:''}
};
const THEME_KEY={};
const SERIES_HERO={};
const SERIES_IMG={};
'''+s[j:]
rep('<span>系列介紹（原廠 27Q3Q4 Convention Sheet）</span>','<span>系列介紹（2XU H2-27 Story，中文說明由艾盟仕整理）</span>',1)

# --- 尺寸 ---
i=s.index("const SHOE=[];"); j=s.index("const SIZE_COLS={};",i)
s=s[:i]+r'''// 2XU 尺寸：一般尺寸 → 襪子 M1/M2/L1/L2 → 加長版（T＝Tall）→ 單一尺寸。每款各自一組（run＝款號），同款各色共用格子
const SZ_ORDER=['XXS','XS','S','M','M1','M2','L','L1','L2','XL','XXL','XXXL','XST','ST','MT','LT','XLT','XXLT','OSFA'];
const RUNS={}; ITEMS.forEach(i=>{ const r=RUNS[i.run]=RUNS[i.run]||[]; i.sizes.forEach(z=>{ if(!r.includes(z)) r.push(z); }); }); for(const k in RUNS) RUNS[k].sort((a,b)=>SZ_ORDER.indexOf(a)-SZ_ORDER.indexOf(b));
const SZ_NUM={};
'''+s[j:]

# --- Excel 訂單本欄位 ---
rep("const FIXED=['KEY','No.','款式圖','實體圖','主題','Drop','品類','性別','款號','中文品名','英文品名','顏色','色號','色碼 SKU','Icon','布料','系列／尺寸','商品概述','商品細節','材質與科技','備註','建議售價(NT$)'];",
    "const FIXED=['KEY','No.','款式圖','實體圖','Story','Drop','品類','性別','款號','中文品名','英文品名','顏色','色號','色碼 SKU','新款／延續','Activity','產地','商品概述','商品細節','備註','建議售價(NT$)'];",1)
i=s.index("      const vals=[it.id,it.no||'',null,null,it.theme||''"); j=s.index('\n',i)
s=s[:i]+"      const vals=[it.id,it.no||'',null,null,it.sheet||'',whenOf(it),it.cat||'',it.gen||'',it.style||'',it.zh||'',it.en,it.color,it.cc||'',it.sku||'',it.season||'',it.act||'',String(it.fab||'').replace(/^產地：/,''),it.ov||'',it.dt||'',[it.note,it.rpBorrow?'【同款實體圖】'+it.rpBorrow:''].filter(Boolean).join('\\n'),it.price||null];"+s[j:]
rep("c.alignment={vertical:k>=15&&k<=20?'top':'middle',wrapText:k>=4};","c.alignment={vertical:k>=17&&k<=19?'top':'middle',wrapText:k>=4};",1)
rep("'ETA':10,'建議售價(NT$)':10};","'ETA':10,'建議售價(NT$)':10,'Story':12,'新款／延續':9,'Activity':9,'產地':9};",1)
rep("const SKIP=/MSRP|韓幣|₩|價|","const SKIP=/MSRP|NT\\$|Story|Activity|新款|延續|產地|價|",1)
rep("document.getElementById('rgs').addEventListener('click',e=>{ const b=e.target.closest('[data-rg]'); if(b) setRefReg(b.dataset.rg); });\n",'',1)
rep('。web=true 時不出現任何韓幣字樣','',1)
rep("const box=$('#acct'); if(!AUTH||adminEditing()){ box.hidden=true; return; }","const box=$('#acct'); if(!AUTH||adminEditing()||!String((window.SDR_CONFIG||{}).SUBMIT_URL||'').trim()){ box.hidden=true; return; }  // 傳單模式（沒設收單網址）不顯示經銷商 Email 驗證列",1)
rep('--bg:#f2f4f8; --surface:#ffffff; --sunk:#e6ebf2; --line:#d2dae6; --fg:#121a26; --muted:#5d6979;','--bg:#f4f4f4; --surface:#ffffff; --sunk:#ebebeb; --line:#d6d6d6; --fg:#141414; --muted:#636363;',1)
rep('--bg:#0b1019; --surface:#131a26; --sunk:#1b2433; --line:#2b384d; --fg:#e8eef7; --muted:#97a5ba;','--bg:#0c0c0c; --surface:#161616; --sunk:#202020; --line:#333333; --fg:#ededed; --muted:#a3a3a3;',2)
rep('--brand:#1c1c1c; --brand-ink:#ffffff; --brand-2:#000000;','--brand:#000000; --brand-ink:#ffffff; --brand-2:#000000;',2)
rep("// 這季目錄都是服裝。大類依品類，跟三個分頁不同：羽絨分頁裡的外套和背心會分開算。\nconst AN_GROUPS=[['上衣',['短袖T恤','長袖T恤','短袖POLO衫','長袖POLO衫']],['外套',['羽絨外套','輕量羽絨外套','外套']],['背心',['羽絨背心','背心']],['長褲',['長褲']]];",
    "// 2XU：大類跟網頁一樣（上身／下身／配件）\nconst AN_GROUPS=[['上身',[]],['下身',[]],['配件',[]]];",1)
rep("  if(!it) return '找不到商品';\n  const cat=String(it.cat||'');","  if(!it) return '找不到商品';\n  return cgOf(it);\n  const cat=String(it.cat||'');",1)
rep("notes?'這季目錄都是服裝，沒有配件和鞋。上衣是 T 恤和 POLO；外套含羽絨外套、輕量羽絨和 GORE-TEX 外套；背心含羽絨背心。':''","notes?'大類跟網頁一樣：上身、下身、配件（袖套、小腿套、襪子、帽款、包款、手套、泳鏡等）。':''",1)
rep("'這季目錄都是服裝，沒有配件和鞋。大類依品類：上衣是 T 恤和 POLO，外套含羽絨外套、輕量羽絨和 GORE-TEX 外套，背心含羽絨背心。款色是款號加顏色；","'大類跟網頁一樣：上身、下身、配件（袖套、小腿套、襪子、帽款、包款、手套、泳鏡等）。款色是款號加顏色；",1)
rep("系列取商品資料的系列欄，寫成「產品線｜主題」，例如 PREMIUM TECH ESSENTIAL｜TOUGH、SNOW｜CANON。訂貨窗口不另外拆開。沒有系列欄的款，改用主題。","系列寫成「Story｜Activity」，例如 Aero｜跑步、X Core｜團體運動。",2)

# --- 2XU 官網高解析圖（of.js，tools/build_official.py）：卡片／放大檢視多一組「商品圖」（去背正面／背面／側面／細節），官網實穿照排在實體圖最前面 ---
rep('data.js?v=20261123a','data.js?v=20261123h',1); rep('imgs.js?v=20261123a','imgs.js?v=20261123h',1)
rep('<script src="rp.js?v=20261123a"></script>','<script src="rp.js?v=20261123h"></script>\n<script src="of.js?v=20261123h"></script>',1)
rep("const hasImg = h=>!!(h&&(IMG[h]||RP[h]));",
"""// 官網圖（of.js X2_OF）：只收款號＋色號與 2XU 官網 SKU 完全相同的款色。p＝商品圖（去背），w＝實穿照（取代借同款實體圖）
const OF = window.X2_OF || {};
ITEMS.forEach(i=>{ const o=OF[i.id]; if(!o) return; if(o.p&&o.p.length){ i.prods=o.p.map(x=>x[0]); i.prodcap=o.p.map(x=>x[1]); }
  if(o.w&&o.w.length){ const keep=!i.rpBorrowOnly; i.photos=[...o.w.map(x=>x[0]),...(keep?(i.photos||[]):[])]; i.phcap=[...o.w.map(x=>x[1]),...(keep?(i.phcap||[]):[])]; i.hasRP=true; i.hasOF=true; if(i.rpBorrowOnly){ i.rpBorrow=''; i.rpBorrowOnly=false; } } });
const lbList=(it,k)=>k==='prod'?(it.prods||[]):k==='photo'?(it.photos||[]):(it.doll?[it.doll]:[]);
const lbCap=(it,k)=>k==='prod'?(it.prodcap||[]):k==='photo'?(it.phcap||[]):[];
const hasImg = h=>!!(h&&(IMG[h]||RP[h]));""",1)
# 資料待更新說明：官網圖
rep("    `尺寸：依原廠訂單表各色開放尺寸",
"""    `官網高解析圖：${ITEMS.filter(i=>i.prods||i.hasOF).length} 款色有 2XU 官網同款同色照片（「商品圖」去背正面／背面／側面 ${ITEMS.filter(i=>i.prods).length} 款色、官網實穿照 ${ITEMS.filter(i=>i.hasOF).length} 款色，長邊約 1400px）；其餘款式圖是原廠訂單表附圖（原檔約 200–300px，原廠沒有更高解析）`,
    `尺寸：依原廠訂單表各色開放尺寸""",1)
# 卡片：有商品圖時卡片主圖用商品圖第一張；按鈕 款式圖／商品圖／實體圖
rep("""  const h = it.doll||ph[0];
  const src = h && IMG[h];
  const sw = `<div class="sw">${it.doll?'<button data-pic="doll">款式圖</button>':''}""",
"""  const pr=it.prods||[];
  const h = pr[0]||(it.hasOF&&ph[0])||it.doll||ph[0];  // 有官網高解析圖時卡片主圖用官網圖
  const src = h && IMG[h];
  const sw = `<div class="sw">${it.doll?'<button data-pic="doll">款式圖</button>':''}${pr.length?`<button data-pic="prod" title="2XU 官網同款同色商品圖（正面／背面／側面）">商品圖${pr.length>1?' '+pr.length:''}</button>`:''}""",1)
rep("""  return `<img src="${h?big(h):src}" alt="${esc(it.en+' '+it.color)}" data-zoom loading""",
    """  return `<img src="${h?big(h):src}" alt="${esc(it.en+' '+it.color)}" data-zoom="${h===pr[0]&&pr.length?'prod':h===it.doll?'doll':'photo'}" loading""",1)
rep("""function openLB(id,kind,ev){ const it=BY[id]; const ph=it.photos||[]; if(kind==='photo'&&!ph.length) kind='doll'; if(kind==='doll'&&!it.doll) kind='photo'; LB=""",
    """function openLB(id,kind,ev){ const it=BY[id]; if(!lbList(it,kind).length) kind=['doll','prod','photo'].find(k=>lbList(it,k).length)||'doll'; LB=""",1)
rep("""  if(!LB||LB.kind!=='photo'){ z.style.width=''; z.style.height=''; return; }
  const it=BY[LB.id], h=(it.photos||[])[LB.i], d=RP[h];""",
    """  if(!LB||LB.kind==='doll'){ z.style.width=''; z.style.height=''; return; }
  const it=BY[LB.id], h=lbList(it,LB.kind)[LB.i], d=RP[h];""",1)
rep("""  const it=BY[LB.id]; const ph=it.photos||[]; const isP=LB.kind==='photo';
  const h=isP?ph[LB.i]:it.doll;""",
    """  const it=BY[LB.id]; const ph=lbList(it,LB.kind); const isP=LB.kind!=='doll'; const pcap=lbCap(it,LB.kind);
  const h=isP?ph[LB.i]:it.doll;""",1)
rep("""  const cap=(isP&&it.phcap&&it.phcap[LB.i])?`<span class="zm-cap">${esc(it.phcap[LB.i])}</span>`:'';""",
    """  const cap=(isP&&pcap[LB.i])?`<span class="zm-cap">${esc(pcap[LB.i])}</span>`:'';""",1)
rep("""  const tabs=(it.doll&&ph.length)?`<div class="zm-tabs"><button data-lbk="doll" aria-pressed="${!isP}">款式圖</button><button data-lbk="photo" aria-pressed="${isP}">實體圖</button></div>`:'';""",
    """  const kinds=[['doll','款式圖'],['prod','商品圖'],['photo','實體圖']].filter(([k])=>lbList(it,k).length);
  const tabs=kinds.length>1?`<div class="zm-tabs">${kinds.map(([k,n])=>`<button data-lbk="${k}" aria-pressed="${LB.kind===k}">${n}</button>`).join('')}</div>`:'';""",1)
rep("""${it.rpBorrow?`<div class="zm-note">${esc(it.rpBorrow)}</div>`:''}<div class="zm-bar">""","""${(it.rpBorrow&&LB.kind==='photo')?`<div class="zm-note">${esc(it.rpBorrow)}</div>`:''}<div class="zm-bar">""",1)
rep("""  if(e.target.closest('[data-zoom]')){ openLB(id,(BY[id].doll?'doll':'photo'),e); }""",
    """  const zm=e.target.closest('[data-zoom]'); if(zm){ openLB(id,zm.dataset.zoom||(BY[id].doll?'doll':'photo'),e); }""",1)
rep("""  if(LB && a){ const n=(BY[LB.id].photos||[]).length; LB.i=""","""  if(LB && a){ const n=lbList(BY[LB.id],LB.kind).length; LB.i=""",1)
rep("""if(LB&&LB.kind==='photo'&&(e.key==='ArrowRight'||e.key==='ArrowLeft')){ const n=(BY[LB.id].photos||[]).length;""",
    """if(LB&&LB.kind!=='doll'&&(e.key==='ArrowRight'||e.key==='ArrowLeft')){ const n=lbList(BY[LB.id],LB.kind).length;""",1)

# --- 中文說明（Marc 11/23）：data.js 的 ov／dt 已是繁中（tools/zh/zh.json），原廠英文在 ovEn／dtEn，細節區可展開「原廠英文說明」 ---
rep("    `商品說明：${nOv}／${nSt} 款附原廠型錄英文說明（點「看商品細節與材質」），中文說明待補`,",
    "    `商品說明：${nOv}／${nSt} 款附原廠型錄說明，已翻成繁體中文（點「看商品細節與材質」；PWX、MCS 等技術名詞保留英文${web?'，原廠英文可在細節區展開':''}），其餘 ${nSt-nOv} 款原廠型錄沒有說明`,",1)
rep("""${it.fab?`<div><h4>材質與版型</h4><p>${esc(it.fab)}</p></div>`:''}</div>`:''}""",
    """${it.fab?`<div><h4>產地</h4><p>${esc(String(it.fab).replace(/^產地：/,''))}</p></div>`:''}${(it.ovEn||it.dtEn)?`<details class="en-src"><summary>原廠英文說明</summary><p>${esc([it.ovEn,it.dtEn].filter(Boolean).join('\\n\\n'))}</p></details>`:''}</div>`:''}""",2)
rep(".detail p{margin:0;white-space:pre-line}",".detail p{margin:0;white-space:pre-line}\n.detail .en-src summary{cursor:pointer;font-size:12px;color:var(--muted)}.detail .en-src p{font-size:12px;color:var(--muted);margin-top:4px}",1)
open(R+'index.html','w').write(s)
print('ok')
