"""2XU 官網（Shopify 公開 products.json）高解析商品圖／實穿照 → big/of_*.jpg＋of.js。

只收「款號＋色號」與官網 SKU 完全相同的款色（同款同色），其餘不放。
  - 商品圖（去背／平拍，無模特兒）：配件類（U 開頭款號，Race Belt 除外）且影像無皮膚色；人工確認後的例外寫在 MANUAL_PROD／MANUAL_SKIP
  - 實穿照：其餘官網照片（模特兒穿著），放進「實體圖」最前面
  - 圖片長邊 >2000px 才縮到 2000；其餘原尺寸，JPEG q90（不放大）
用法：
  python3 tools/build_official.py --fetch   # 重抓官網 products.json（www/us/uk/nz）→ tools/official/index.json
  python3 tools/build_official.py           # 依 index.json 下載（快取 sources/official/，不進 git）並產 big/of_*.jpg、of.js
build_data.py 會清空 big/，所以重產順序：build_data.py → build_official.py。
"""
import json, os, re, sys, io, glob, time, hashlib, collections, urllib.request
import numpy as np
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIG = os.path.join(R, 'big'); CACHE = os.path.join(R, 'sources', 'official'); IDX = os.path.join(R, 'tools', 'official', 'index.json')
HOSTS = ['www.2xu.com', 'us.2xu.com', 'uk.2xu.com', 'nz.2xu.com']
SK = re.compile(r'^([A-Z]{2}\d{4}[A-Z]?)-([A-Z0-9]+/[A-Z0-9]+)')
NOT_PROD_STYLES = {'UQ3800G'}            # Race Belt：官網照片都是腰上穿著
MANUAL_PROD = {'UA5043e_DYP-GRY_1_', 'UA5043e_DYP-GRY_2_', 'UA5043e_DYP-GRY_3_', 'UA5155e_HPK-GRY-2_', 'UQ7149k_AMB-CLR_4_'}  # 粉紅／膚色系商品被判成皮膚，人工看過是去背商品圖
MANUAL_SKIP = set()
UA = {'User-Agent': 'Mozilla/5.0'}


def get(u, t=60):
    for k in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()
        except Exception as e:
            err = e; time.sleep(2 + k * 3)
    raise err


def items():
    s = open(os.path.join(R, 'data.js'), encoding='utf-8').read()
    return json.loads(s[s.index('['):s.rindex(']') + 1])


def fetch():
    want = {(d['style'].upper(), d['cc'].upper()) for d in items()}
    idx = collections.defaultdict(list); seen = collections.defaultdict(set)
    for host in HOSTS:
        page = 1
        while True:
            P = json.loads(get(f'https://{host}/products.json?limit=250&page={page}'))['products']
            if not P: break
            for p in P:
                vc = {}
                for v in p['variants']:
                    m = SK.match((v.get('sku') or '').upper())
                    if m: vc[v['id']] = (m.group(1), m.group(2))
                cols = set(vc.values())
                for im in p['images']:
                    fn = im['src'].split('?')[0].split('/')[-1]; F = fn.upper().replace('_', '-')
                    if len(cols) == 1: hit = list(cols)
                    else:
                        hit = [c for c in cols if c[1].replace('/', '-') in F or c[1].replace('/', '') in F]
                        if len(hit) != 1:
                            hv = {vc[i] for i in im.get('variant_ids', []) if i in vc}
                            if len(hv) == 1: hit = list(hv)
                    if len(hit) != 1 or hit[0] not in want: continue
                    m = re.match(r'([A-Z]{2}\d{4}[A-Z]?)', F)
                    if m and m.group(1) != hit[0][0]: continue   # 檔名寫的款號不同就不收
                    k = '|'.join(hit[0])
                    if fn in seen[k]: continue
                    seen[k].add(fn)
                    idx[k].append(dict(src=im['src'].split('?')[0], fn=fn, w=im['width'], h=im['height'], pos=im['position'], host=host, handle=p['handle'], title=p['title']))
            page += 1; time.sleep(.4)
    os.makedirs(os.path.dirname(IDX), exist_ok=True)
    json.dump({'fetched': time.strftime('%Y-%m-%d %H:%M'), 'hosts': HOSTS, 'items': idx}, open(IDX, 'w'), ensure_ascii=False, indent=0)
    print('index', len(idx), '款色', sum(len(v) for v in idx.values()), '張')


def dh(I):
    a = np.asarray(I.convert('L').resize((17, 16)), dtype=int); return (a[:, 1:] > a[:, :-1]).flatten()


def skin(I):
    a = np.asarray(I.convert('YCbCr').resize((150, 187))).astype(int); Y, Cb, Cr = a[..., 0], a[..., 1], a[..., 2]
    return float(((Cr >= 135) & (Cr <= 175) & (Cb >= 80) & (Cb <= 125) & (Y > 60)).mean())


def closeup(I):
    """商品碰到 2 邊以上＝特寫（細節）。用邊框 8px 內的亮度梯度判斷（背景是平滑漸層）。"""
    a = np.asarray(I.convert('L').resize((300, 373)), dtype=float)
    gx = np.abs(np.diff(a, axis=1)); gy = np.abs(np.diff(a, axis=0))
    sides = [gx[:8].mean() + gy[:8].mean(), gx[-8:].mean() + gy[-8:].mean(), gx[:, :8].mean() + gy[:, :8].mean(), gx[:, -8:].mean() + gy[:, -8:].mean()]
    return sum(s > 3.0 for s in sides) >= 2


def build():
    idx = json.load(open(IDX))['items']
    os.makedirs(CACHE, exist_ok=True); os.makedirs(BIG, exist_ok=True)
    for f in glob.glob(os.path.join(BIG, 'of_*.jpg')): os.remove(f)
    OF, DIM, log = {}, {}, []
    host_rank = {h: i for i, h in enumerate(HOSTS)}
    for d in items():
        k = f"{d['style'].upper()}|{d['cc'].upper()}"
        L = sorted(idx.get(k, []), key=lambda x: (host_rank[x['host']], x['pos']))
        if not L: continue
        keep = []
        for x in L:
            cp = os.path.join(CACHE, hashlib.md5(x['src'].encode()).hexdigest()[:16] + '.jpg')
            if not os.path.exists(cp): open(cp, 'wb').write(get(x['src']))
            I = Image.open(cp); I.load(); I = I.convert('RGB')
            h = dh(I)
            dup = next((y for y in keep if (h != y['dh']).sum() <= 12), None)
            if dup is not None:
                if I.width * I.height > dup['I'].width * dup['I'].height: dup.update(I=I, x=x)
                continue
            keep.append(dict(I=I, x=x, dh=h))
        prods, wears = [], []
        for y in keep:
            I, x = y['I'], y['x']; tag = x['fn']
            if any(m in tag for m in MANUAL_SKIP): continue
            st = d['style'].upper()
            isp = any(m in tag for m in MANUAL_PROD) or (st.startswith('U') and st not in NOT_PROD_STYLES and skin(I) < 0.004)
            (prods if isp else wears).append(y)
        n = 0
        def save(y, kind):
            nonlocal n
            I = y['I']
            if max(I.size) > 2000: I = I.copy(); I.thumbnail((2000, 2000), Image.LANCZOS)
            key = 'of_' + re.sub(r'[^A-Za-z0-9]+', '_', d['id']).strip('_').lower() + f'_{kind}{n}'; n += 1
            I.save(os.path.join(BIG, key + '.jpg'), quality=90, subsampling=0, optimize=True)
            DIM[key] = list(I.size); return key
        cap_cap = ['側面', '正面', '背面']
        is_cap = re.search(r'\b(Cap|Visor)\b', d['en'], re.I)
        cu = [closeup(y['I']) for y in prods]
        nfull = cu.count(False)
        P, j = [], 0
        for y, c0 in zip(prods, cu):
            if c0: c = '細節特寫'
            elif is_cap: c = cap_cap[j] if j < 3 else '細節特寫'; j += 1
            elif nfull == 1: c = '商品圖'
            else: j += 1; c = f'角度 {j}'
            P.append([save(y, 'p'), ('' if c == '商品圖' else '商品圖・') + c + '（2XU 官網，同款同色）'])
        W = [[save(y, 'w'), '實穿照（2XU 官網，同款同色）'] for y in wears]
        OF[d['id']] = {k2: v for k2, v in (('p', P), ('w', W)) if v}
        log.append([d['id'], d['style'], d['cc'], len(P), len(W), keep[0]['x']['handle']])
    js = ('// 2XU 官網高解析圖：X2_OF 款色 id → {p:[[圖檔鍵, 說明]] 商品圖（去背）, w:[[圖檔鍵, 說明]] 實穿照}；X2_OFD 圖檔鍵→[寬,高]。tools/build_official.py 產生，'
          + time.strftime('%Y-%m-%d') + '。只收款號＋色號與官網 SKU 完全相同的款色。\n'
          + 'window.X2_OF=' + json.dumps(OF, ensure_ascii=False, separators=(',', ':')) + ';\n'
          + 'window.X2_OFD=' + json.dumps(DIM, separators=(',', ':')) + ';\n'
          + 'window.X2_RP=Object.assign(window.X2_RP||{},window.X2_OFD);\n')
    open(os.path.join(R, 'of.js'), 'w', encoding='utf-8').write(js)
    import csv
    with open(os.path.join(R, 'tools', 'match', 'official.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['款色 id', '款號', '色號', '商品圖張數', '實穿照張數', '官網商品頁 handle']); w.writerows(log)
    print('款色', len(OF), '商品圖款色', sum(1 for v in OF.values() if 'p' in v), '商品圖', sum(len(v.get('p', [])) for v in OF.values()), '實穿照', sum(len(v.get('w', [])) for v in OF.values()), '張')


if __name__ == '__main__':
    fetch() if '--fetch' in sys.argv else build()
