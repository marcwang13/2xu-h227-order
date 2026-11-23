"""圖片畫質統計（前後對比）：每款色「最清楚的一張」長邊與 Laplacian 清晰度（縮放到放大檢視高度 600px 後計算，模擬瀏覽器看到的樣子）。
before＝款式圖（訂單表）＋自己的型錄照；after＝再加官網商品圖／實穿照。輸出 tools/match/hq_stats.json、hq_unimproved.csv。"""
import json, os, re, csv, collections
import numpy as np
from PIL import Image, ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def js(name, var):
    s = open(os.path.join(R, name), encoding='utf-8').read()
    m = re.search(r'window\.' + var + r'=(\{.*?\});', s, re.S); return json.loads(m.group(1)) if m else {}
s = open(os.path.join(R, 'data.js'), encoding='utf-8').read(); D = json.loads(s[s.index('['):s.rindex(']') + 1])
RPI = js('rp.js', 'X2_RPI'); OF = js('of.js', 'X2_OF')
LAP = ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], 1, 128)
cache = {}
def info(k):
    if k not in cache:
        I = Image.open(os.path.join(R, 'big', k + '.jpg')).convert('L')
        sc = 600 / I.height; J = I.resize((max(1, round(I.width * sc)), 600), Image.BICUBIC)
        a = np.asarray(J.filter(LAP), dtype=float) - 128
        cache[k] = (max(I.size), float(a.var()))
    return cache[k]
rows = []; dist_b = collections.Counter(); dist_a = collections.Counter()
for d in D:
    b = ([d['doll']] if d.get('doll') else []) + [x[0] for x in RPI.get(d['id'], [])]
    o = OF.get(d['id'], {}); a = b + [x[0] for x in o.get('p', []) + o.get('w', [])]
    bb = max((info(k) for k in b), default=(0, 0)); ab = max((info(k) for k in a), default=(0, 0))
    rows.append(dict(id=d['id'], style=d['style'], cc=d['cc'], en=d['en'], color=d['color'], b_long=bb[0], a_long=ab[0], b_lap=round(bb[1], 1), a_lap=round(ab[1], 1), prod=len(o.get('p', [])), wear=len(o.get('w', []))))
    f = lambda n: '<300' if n < 300 else '300-599' if n < 600 else '600-999' if n < 1000 else '1000+'
    dist_b[f(bb[0])] += 1; dist_a[f(ab[0])] += 1
imp = [r for r in rows if r['a_long'] > r['b_long']]
st = dict(款色=len(rows), 提升款色=len(imp), 提升比例=round(len(imp) / len(rows) * 100, 1), 有商品圖款色=sum(1 for r in rows if r['prod']), 有官網實穿照款色=sum(1 for r in rows if r['wear']),
          長邊分佈_before=dict(dist_b), 長邊分佈_after=dict(dist_a),
          Laplacian中位數_提升款色_before=float(np.median([r['b_lap'] for r in imp])) if imp else None,
          Laplacian中位數_提升款色_after=float(np.median([r['a_lap'] for r in imp])) if imp else None,
          未提升款色=len(rows) - len(imp))
json.dump(st, open(os.path.join(R, 'tools', 'match', 'hq_stats.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(R, 'tools', 'match', 'hq_unimproved.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['款色 id', '款號', '色號', '英文品名', '顏色', '目前最清楚一張長邊(px)', '原因'])
    for r in rows:
        if r['a_long'] <= r['b_long']:
            w.writerow([r['id'], r['style'], r['cc'], r['en'], r['color'], r['b_long'], '官網沒有同款同色（H2-27 新款號／新色尚未上架）；訂單表與型錄 PDF 內嵌原圖即此解析度'])
print(json.dumps(st, ensure_ascii=False, indent=1))
