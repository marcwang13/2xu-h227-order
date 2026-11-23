#!/usr/bin/env python3
"""2XU H2-27 正式訂貨：從原廠訂單表（xlsx）＋型錄（PDF）產生 data.js、imgs.js、rp.js、big/ 圖檔與對圖清單。

用法（在 repo 根目錄）：
  python3 tools/build_data.py --xlsx sources/2XU_H2-27_order_form.xlsx --pdf sources/2XU_H2-27_catalogue.pdf

- 一筆 data.js 商品＝一個款色（Style Code＋Colour），卡片＝一款（同 Style Code）。
- 款式圖（doll）：原廠訂單表「圖片」欄內嵌圖，依圖片錨點列對到款色，存 big/<md5前12>.jpg。
- 實體圖（photos）：型錄商品頁的實穿照（PDF 內嵌 JPEG 原檔，不重新壓縮），依照片右上角色碼標籤＋下方款號對到款色，
  存 big/cp_p<頁>_<xref>.jpg；對應表寫 rp.js（X2_RP 寬高、X2_RPI 款色→[[圖, 說明]]、X2_RPB 同款借圖）。
- 價格＝NTD MSRP（台灣建議售價）。Drop 只顯示 Drop 1／2／3（Marc 11/23：不放月份）。
- sources/ 不進 git（原廠檔）。
"""
import argparse, collections, csv, hashlib, io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fix_text  # 型錄英文黏字補空格
import openpyxl
import pymupdf as fitz
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--xlsx', default='sources/2XU_H2-27_order_form.xlsx')
ap.add_argument('--pdf', default='sources/2XU_H2-27_catalogue.pdf')
ap.add_argument('--out', default='.')
A = ap.parse_args()
OUT = A.out
BIG = os.path.join(OUT, 'big'); os.makedirs(BIG, exist_ok=True)
MATCH = os.path.join(OUT, 'tools', 'match'); os.makedirs(MATCH, exist_ok=True)


GEN = {'Mens': '男', 'Womens': '女', 'Unisex': '中性'}
SZ_ORDER = ['XXS', 'XS', 'S', 'M', 'M1', 'M2', 'L', 'L1', 'L2', 'XL', 'XXL', 'XXXL', 'XST', 'ST', 'MT', 'LT', 'XLT', 'XXLT', 'OSFA']
ACC_CATS = {'袖套', '小腿套', '襪子', '帽子', '遮陽帽', '後背包', '其他', '手套', '泳鏡'}

# ---------- 1. 原廠訂單表 ----------
wb = openpyxl.load_workbook(A.xlsx)
ws = wb.worksheets[0]
assert ws.cell(7, 2).value == 'Style Code' and ws.cell(7, 15).value == 'NTD MSRP', '訂單表欄位跟預期不同（第 7 列標題）'
cws, cur = [], None
for r in range(8, ws.max_row + 1):
    v = [ws.cell(r, c).value for c in range(1, 19)]
    if not v[1]:
        continue
    key = (str(v[0]), v[1].strip(), str(v[9]).strip())
    if cur is None or cur['_key'] != key:
        cur = dict(_key=key, no=v[0], style=v[1].strip(), season=v[3], gender=v[4], name=v[5], act=v[6], story=v[7],
                   en=str(v[8]).strip(), cc=str(v[9]).strip(), cdesc=str(v[10]).strip(), drop=v[13], price=v[14],
                   coo=v[17], r0=r, r1=r, sizes=[], bar={})
        cws.append(cur)
    cur['r1'] = r
    sz = str(v[11]).strip()
    cur['sizes'].append(sz)
    cur['bar'][sz] = str(v[12]).strip()

# 款式圖：圖片錨點（左上角列）落在哪個款色的列範圍
flat = {}
for im in ws._images:
    a = im.anchor
    if type(a).__name__ != 'TwoCellAnchor':
        continue
    top = a._from.row + 1
    hit = [c for c in cws if c['r0'] <= top <= c['r1']]
    if not hit:
        continue
    data = im._data()
    h = hashlib.md5(data).hexdigest()[:12]
    I = Image.open(io.BytesIO(data))
    if I.mode in ('RGBA', 'LA', 'P'):
        I = I.convert('RGBA'); bg = Image.new('RGB', I.size, 'white'); bg.paste(I, mask=I.split()[3]); I = bg
    else:
        I = I.convert('RGB')
    I.save(os.path.join(BIG, h + '.jpg'), quality=94, subsampling=0)
    flat.setdefault(id(hit[0]), []).append((h, I.size))
FLATDIM = {}
for c in cws:
    f = flat.get(id(c), [])
    c['doll'] = f[0][0] if f else ''
    if f:
        FLATDIM[f[0][0]] = list(f[0][1])

# ---------- 2. 型錄照片 ----------
doc = fitz.open(A.pdf)
CODE = re.compile(r'^[MWUY][A-Z]\d{4}[A-Z]$')
TOK = re.compile(r'^[A-Z]{2,4}$')
styles = collections.defaultdict(dict)
for c in cws:
    styles[c['style'].upper()][c['cc'].upper()] = c


def norm_tag(code, raw):
    cols = styles.get(code, {})
    raw = raw.replace('/', '')
    hit = [k for k in cols if k.replace('/', '') == raw]
    if hit:
        return hit[0]
    hit = [k for k in cols if len(raw) >= 5 and k.replace('/', '').startswith(raw)]  # 標籤字被截斷（例 CTTDB → CTT/DBF）
    return hit[0] if len(hit) == 1 else None


def load_rgb(x):
    """PDF 內嵌圖轉 RGB；有 SMask（去背）就疊在白底上。"""
    pix = fitz.Pixmap(doc, x)
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.n >= 4:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    I = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
    sm = doc.xref_get_key(x, 'SMask')
    if sm[0] == 'xref':
        mx = int(sm[1].split()[0])
        mp = fitz.Pixmap(doc, mx)
        M = Image.open(io.BytesIO(mp.tobytes('png'))).convert('L')
        if M.size != I.size:
            M = M.resize(I.size, Image.LANCZOS)
        if M.getextrema()[0] < 250:  # 真的有透明區才合成
            bg = Image.new('RGB', I.size, (255, 255, 255)); bg.paste(I, mask=M); I = bg
    return I


def save_photo(x, path):
    sm = doc.xref_get_key(x, 'SMask')
    img = doc.extract_image(x)
    if sm[0] != 'xref' and img['ext'] in ('jpeg', 'jpg') and Image.open(io.BytesIO(img['image'])).mode == 'RGB':
        open(path, 'wb').write(img['image'])  # 原檔 JPEG，不重新壓縮
    else:
        load_rgb(x).save(path, quality=95, subsampling=0)


_isp = {}
def is_photo(x):
    if x not in _isp:
        try:
            I = load_rgb(x); I.thumbnail((128, 128))
            from PIL import ImageStat
            from PIL import ImageFilter
            edge = ImageStat.Stat(I.convert('L').filter(ImageFilter.FIND_EDGES)).mean[0]
            _isp[x] = sum(ImageStat.Stat(I).stddev) / 3 > 17 or edge > 12
        except Exception:
            _isp[x] = False
    return _isp[x]


photos = []      # 每張有色碼標籤、款號對得到的照片
unused = []      # 型錄照片對不到台灣訂單表的紀錄
_seen = set()
desc = {}        # 款號 → (名稱, 說明, 條列)
for pn in range(len(doc)):
    p = doc[pn]
    lines = []
    for b in p.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            t = ''.join(s['text'] for s in l['spans']).strip()
            if t:
                lines.append((t, fitz.Rect(l['bbox'])))
    codes = [(t.replace(' ', '').upper(), r) for t, r in lines if CODE.match(t.replace(' ', '').upper())]
    if not codes:
        continue
    # 商品說明：款號下方同欄的文字
    for code, r in codes:
        if code in desc or code not in styles:
            continue
        col = [(t, rr) for t, rr in lines if rr.y0 > r.y1 - 1 and r.x0 - 10 <= rr.x0 < r.x0 + 320 and rr.y0 < 560 and rr.y0 < r.y1 + 160]
        col.sort(key=lambda x: (round(x[1].y0), x[1].x0))
        name, para, bullets = None, [], []
        for t, rr in col:
            if CODE.match(t.replace(' ', '').upper()) or (TOK.match(t) and bullets):
                break
            if t in ('®', '™', '+') or re.fullmatch(r'\d{1,3}', t):
                continue
            if name is None:
                name = t; continue
            if t.startswith('•'):
                bullets.append(t.lstrip('• ').strip())
            elif bullets:
                bullets[-1] += ' ' + t
            elif not TOK.match(t):
                para.append(t)
        if name and (para or bullets) and len(code) and abs(r.y0 - 405) < 60:
            desc[code] = (name, fix_text.fix(' '.join(para).replace(' ®', '®')), [fix_text.fix(x) for x in bullets], pn + 1)
    letters = [(t.replace(' ', ''), r) for t, r in lines if re.fullmatch(r'[A-Z ]{1,6}', t) and r.height < 12]
    toks = [(t, r) for t, r in lines if TOK.match(t) and r.height < 12]
    tags = []
    for i, (t, r) in enumerate(toks):
        for j, (t2, r2) in enumerate(toks):
            if i != j and abs((r.x0 + r.x1) / 2 - (r2.x0 + r2.x1) / 2) < 5 and 5 < r2.y0 - r.y0 < 11:
                tags.append((t + '/' + t2, fitz.Rect(r) | r2))
    infos = [i for i in p.get_image_info(xrefs=True) if i['xref'] and i['width'] >= 100 and fitz.Rect(i['bbox']).width < 700]
    R_ = [fitz.Rect(i['bbox']) for i in infos]
    ov = lambda a, b: (a & b).get_area() / max(1e-6, min(a.get_area(), b.get_area()))
    # 跨好幾格的底圖／遮罩（同時蓋到 2 張以上彼此不重疊的圖）不算照片
    span = set()
    for k, a in enumerate(R_):
        oth = [j for j, b in enumerate(R_) if j != k and (a & b).get_area() > 0.25 * b.get_area()]
        if any(ov(R_[x], R_[y]) < 0.3 for x in oth for y in oth if x < y):
            span.add(k)
    keep, used = [], set()
    for k, info in enumerate(infos):  # 同一格疊兩張圖（漸層底圖＋照片）時留最上層
        if k in used or k in span:
            continue
        grp = [j for j in range(len(infos)) if j not in span and j not in used and ov(R_[k], R_[j]) > 0.6]
        used.update(grp)
        keep.append(infos[max(grp)])  # 後畫的在上層＝看得到的那張
    for info in keep:
        x = info['xref']
        if not x:
            continue
        bb = fitz.Rect(info['bbox'])
        # 畫質門檻：型錄 PDF 已壓縮，長邊不到 220px 的照片不比訂單表款式圖清楚，不用
        if bb.width < 60 or bb.height < 60 or info['width'] < 150 or bb.width > 700:
            continue
        if not is_photo(x):  # 照片上面疊的漸層遮罩（近乎單色）不算
            continue
        # 色碼標籤：照片右上角的小方塊，2～3 行大寫字（例 BLK/SRF、BLK/TT/M、MD/N/MD/N），合併後跟這款的台灣色碼比對
        tg_lines = sorted([(r.y0, r.x0, t) for t, r in letters if bb.x1 - 48 <= (r.x0 + r.x1) / 2 <= bb.x1 + 18 and bb.y0 - 18 <= (r.y0 + r.y1) / 2 <= bb.y0 + 42])
        tagraw = ''.join(t for _, _, t in tg_lines)
        cand = [(c, r) for c, r in codes if r.y0 >= max(bb.y1 - 20, (bb.y0 + bb.y1) / 2) and r.x0 - 12 <= bb.x0]
        code = None
        if cand:
            miny = min(r.y0 for c, r in cand)
            row = [(c, r) for c, r in cand if r.y0 < miny + 6]
            code = max(row, key=lambda cr: cr[1].x0)[0]
        if (pn, x) in _seen:
            continue
        _seen.add((pn, x))
        rec = dict(page=pn + 1, xref=x, bbox=[round(v, 1) for v in bb], w=info['width'], h=info['height'], tag=tagraw, code=code or '')
        cc = norm_tag(code, tagraw) if (code and tagraw) else None
        lowres = max(info['width'], info['height']) < 220
        if cc and not lowres:
            rec['cc'] = cc
            photos.append(rec)
        else:
            rec['why'] = ('畫質太低（長邊<220px，不比訂單表款式圖清楚）' if lowres and code in styles else
                          '款號不在台灣訂單表' if code and code not in styles else
                          '沒有色碼標籤（細節／背面照）' if not tagraw else
                          '沒有對到款號' if not code else '色碼不在這款的台灣訂單顏色')
            unused.append(rec)

# 人工指定：型錄照片沒有色碼標籤（同頁只有單色去背商品照），目視後指定款色。key＝"p<頁>_<xref>"，值＝款色 id；"" 表示不用
OVR_PATH = os.path.join(OUT, 'tools', 'photo_override.json')
OVR = json.load(open(OVR_PATH)) if os.path.exists(OVR_PATH) else {}
_id2 = {c['style'].upper() + '-' + c['cc'].replace('/', '_'): c for c in cws}
for o in list(unused):
    k = 'p%d_%d' % (o['page'], o['xref'])
    if OVR.get(k) in _id2:
        c = _id2[OVR[k]]
        o['code'], o['cc'], o['manual'] = c['style'].upper(), c['cc'].upper(), True
        photos.append(o); unused.remove(o)

RP, RPI = {}, collections.defaultdict(list)
photos.sort(key=lambda o: (o['page'], o['bbox'][1], o['bbox'][0]))
for o in photos:
    key = 'cp_p%03d_%d' % (o['page'], o['xref'])
    path = os.path.join(BIG, key + '.jpg')
    save_photo(o['xref'], path)
    W, H = Image.open(path).size
    RP[key] = [W, H]
    c = styles[o['code']][o['cc']]
    RPI[c['style'].upper() + '-' + c['cc'].replace('/', '_')].append([key, ('型錄商品照（p.%d）' if o.get('manual') or c['name'][:3] not in ('(a)', '(b)') else '型錄實穿照（p.%d）') % o['page']])

# ---------- 3. 組 data.js ----------
def cat_of(name):
    return re.sub(r'^\([a-z]\)\s*', '', name or '').strip()

def letter(name):
    m = re.match(r'^\(([a-z])\)', name or '')
    return m.group(1) if m else ''

BAD_EN = re.compile(r"[a-z][A-Z]|\d[A-Z][a-z]|\bComp\b|\bSht|\bShts\b|\bSeaml\b|Rday|\bLS\b|Compressio$|\bIn\b|^.{30}(?<!s)$")
items = []
ids = set()
for c in cws:
    cid = c['style'].upper() + '-' + c['cc'].replace('/', '_')
    assert cid not in ids, cid
    ids.add(cid)
    cat = cat_of(c['name'])
    acc = cat in ACC_CATS
    lt = letter(c['name'])
    d = desc.get(c['style'].upper())
    it = dict(id=cid, sheet=c['story'], no=c['no'], style=c['style'], en=c['en'],
              zh=f"{GEN.get(c['gender'], '')}款{cat}" if c['gender'] != 'Unisex' else f"中性{cat}",
              color=c['cdesc'], cc=c['cc'], sku=f"{c['style']}-{c['cc']}", cat=cat, gen=GEN.get(c['gender'], ''),
              mon=c['drop'] or '', theme='', act=c['act'], season='新款' if c['season'] == '2027 H2' else '延續款', drop=c['drop'] or '',
              price=int(c['price'] or 0), sizes=sorted(c['sizes'], key=lambda z: SZ_ORDER.index(z) if z in SZ_ORDER else 99), run=c['style'].upper(),
              part='bottom' if lt == 'b' and not acc else 'top', div='ACC' if acc else 'APP',
              fab=f"產地：{c['coo']}" if c['coo'] else '', doll=c['doll'],
              series=f"{c['story']}｜{c['act']}")
    # 原廠訂單表品名常被截斷或縮寫（例 LightSpeedReactHi-RiseCompShts、Light Speed Hi-Rise Compressio），有型錄品名就換成型錄的完整品名
    if d and d[0] and BAD_EN.search(it['en']):
        it['en_form'] = it['en']
        it['en'] = fix_text.fix(d[0]).replace(' inch ', ' Inch ')
    if d:
        it['ov'] = d[1]
        it['dt'] = '\n'.join('・' + b for b in d[2])
        it['catp'] = d[3]
    items.append(it)

# 同款各色品名統一（原廠訂單表同款不同列寫法不一，例 Aero Tee／Aero Mesh Tee）：取最長、沒被截斷的那個
_names = collections.defaultdict(list)
for it in items:
    _names[it['style']].append(it['en'])
for it in items:
    good = [n for n in _names[it['style']] if not BAD_EN.search(n)] or _names[it['style']]
    best = max(good, key=len)
    if it['en'] != best:
        it.setdefault('en_form', it['en'])
        it['en'] = best

# 款式圖缺：借同款其他顏色的款式圖（標示）
bystyle = collections.defaultdict(list)
for it in items:
    bystyle[it['style']].append(it)
for it in items:
    if it['doll']:
        continue
    sib = [x for x in bystyle[it['style']] if x['doll']]
    if sib:
        s = sib[0]
        it['doll'] = s['doll']
        it['dollBorrow'] = f"款式圖為同款 {s['color']}({s['cc']}) 供參考，顏色不同"
    elif RPI.get(it['id']):
        pass  # 沒款式圖但有型錄照：卡片直接顯示型錄照

# 原廠訂單表同一張款式圖貼給同款兩個顏色（例 UQ5685f / UQ6165f 的 BYW/VTF 用了粉色 FSA 的圖）：第一個顏色以外標示借圖
_first = {}
for it in items:
    if not it['doll'] or it.get('dollBorrow'):
        continue
    k = (it['style'], it['doll'])
    if k in _first:
        s = _first[k]
        it['dollBorrow'] = f"款式圖為同款 {s['color']}({s['cc']}) 供參考，顏色不同（原廠訂單表兩色貼同一張圖）"
    else:
        _first[k] = it

# 實體圖缺：借同款其他顏色的型錄照（WHL build_imgref 寫法）
RPB = {}
for it in items:
    if RPI.get(it['id']):
        continue
    sib = [x for x in bystyle[it['style']] if RPI.get(x['id'])]
    if sib:
        s = sib[0]
        RPB[it['id']] = [s['id'], f"實際商品為 {it['color']}({it['cc']})，實體圖為同款 {s['color']}({s['cc']}) 款式供參考，顏色不同"]

# 單色款式圖錯配檢查用：同一張款式圖被幾個款色用
dc = collections.Counter(it['doll'] for it in items if it['doll'] and not it.get('dollBorrow'))

# 縮圖 imgs.js（卡片載入 big/ 失敗時的備援，也供 hasImg 判斷）
IMG = {}
for h in sorted(set(it['doll'] for it in items if it['doll'])):
    I = Image.open(os.path.join(BIG, h + '.jpg')); I.thumbnail((110, 110), Image.LANCZOS)
    b = io.BytesIO(); I.save(b, 'JPEG', quality=72)
    import base64
    IMG[h] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

stamp = '2026-11-23'
with open(os.path.join(OUT, 'data.js'), 'w') as f:
    f.write(f'// 2XU H2-27 正式訂貨商品資料（{len(items)} 款色／{len(bystyle)} 款），由 tools/build_data.py 產生，{stamp}。\n')
    f.write('window.SDR_ITEMS=' + json.dumps(items, ensure_ascii=False) + ';\n')
with open(os.path.join(OUT, 'imgs.js'), 'w') as f:
    f.write('window.SDR_IMG=' + json.dumps(IMG) + ';\n')
with open(os.path.join(OUT, 'rp.js'), 'w') as f:
    f.write(f'// 型錄實穿照：X2_RP 圖檔鍵→[寬,高]；X2_RPI 款色 id→[[圖檔鍵, 說明]]；X2_RPB 款色 id→[借用款色 id, 說明]。tools/build_data.py 產生，{stamp}。\n')
    f.write('window.X2_RP=' + json.dumps(RP) + ';\n')
    f.write('window.X2_RPI=' + json.dumps(dict(RPI), ensure_ascii=False) + ';\n')
    f.write('window.X2_RPB=' + json.dumps(RPB, ensure_ascii=False) + ';\n')
    f.write('window.X2_FLATDIM=' + json.dumps(FLATDIM) + ';\n')

# ---------- 4. 清單 ----------
with open(os.path.join(MATCH, 'match.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['款色 id', '原廠#', '款號', '英文品名', '色碼', '顏色', '款式圖', '款式圖來源', '型錄照張數', '型錄照', '借圖'])
    for it in items:
        ph = RPI.get(it['id'], [])
        w.writerow([it['id'], it['no'], it['style'], it['en'], it['cc'], it['color'], it['doll'],
                    it.get('dollBorrow', '訂單表內嵌圖' if it['doll'] else '無'), len(ph), ' '.join(k for k, _ in ph),
                    RPB.get(it['id'], ['', ''])[1]])
with open(os.path.join(MATCH, 'unmatched_items.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['款色 id', '原廠#', '款號', '英文品名', '色碼', '顏色', '款式圖', '型錄照', '說明'])
    for it in items:
        own = bool(RPI.get(it['id']))
        if own and it['doll'] and not it.get('dollBorrow'):
            continue
        why = []
        if not it['doll']:
            why.append('沒有款式圖（同款也沒有）')
        elif it.get('dollBorrow'):
            why.append('款式圖借同款')
        if not own:
            why.append('型錄沒有這色的照片' + ('，已借同款' if it['id'] in RPB else '，同款也沒有'))
        w.writerow([it['id'], it['no'], it['style'], it['en'], it['cc'], it['color'], '有' if it['doll'] else '無',
                    '自有' if own else ('借同款' if it['id'] in RPB else '無'), '；'.join(why)])
with open(os.path.join(MATCH, 'catalogue_photos_unused.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['頁', 'xref', '人工指定鍵', '款號', '色碼標籤', '原因'])
    for o in unused:
        w.writerow([o['page'], o['xref'], 'p%d_%d' % (o['page'], o['xref']), o['code'], o['tag'], o['why']])

nS = len(bystyle)
st = dict(款數=nS, 款色數=len(items), 尺寸SKU=sum(len(i['sizes']) for i in items),
          有款式圖款色=sum(1 for i in items if i['doll']), 款式圖借同款=sum(1 for i in items if i.get('dollBorrow')),
          無款式圖款色=sum(1 for i in items if not i['doll']),
          有自有型錄照款色=sum(1 for i in items if RPI.get(i['id'])), 型錄照借同款款色=len(RPB),
          完全無型錄照款色=sum(1 for i in items if not RPI.get(i['id']) and i['id'] not in RPB),
          有型錄照款數=len({i['style'] for i in items if RPI.get(i['id'])}),
          型錄照張數=len(RP), 有原廠說明款數=len({i['style'] for i in items if i.get('ov') or i.get('dt')}),
          型錄照片未使用=len(unused))
json.dump(st, open(os.path.join(MATCH, 'stats.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(st, ensure_ascii=False, indent=1))
