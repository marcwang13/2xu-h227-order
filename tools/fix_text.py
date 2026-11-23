"""型錄 PDF 文字是左右對齊排版，抽出來常黏字（例 Powerthrougheverysession、TheForm StashHi-Rise）。
這裡把英文說明補回空格：句讀後補空格、大小寫交界拆開、字典查不到的長字用 wordninja 切。"""
import re
import wordninja

WC = wordninja.DEFAULT_LANGUAGE_MODEL._wordcost
PROTECT = {'wicking', 'plantar', 'kinesiology', 'tencel', 'pilates', 'coolmax', 'ecomade', 'polygiene', 'merino',
           'hi-rise', 'quick-dry', 'sweat-wicking', 'anti-chafe', 'drawcord', 'stash', 'racerback', 'thermoregulation',
           'antimicrobial', 'reflectivity', 'breathability', 'packable', 'chafing', 'zoned', 'ventilated', 'bonded',
           'abrasion', 'compressive', 'longline', 'muscle-mapping', 'microclimate', 'odour', 'stabilise', 'stabilises',
           'unlined', 'flatlock', 'airflow', 'ultralight', 'elasticated', 'sweatband', 'eyewear', 'clearheaded', 'thumbholes', 'thumbhole', 'touchscreen', 'headband', 'headbands', 'waistband', 'drawstring', 'midlayer', 'baselayer', 'zipper', 'softshell', 'windproof', 'waterproof', 'sweatbands', 'optimise', 'optimised', 'minimise', 'minimises', 'colour', 'colours', 'recycled', 'lightweight', 'upf'}
CAMEL_KEEP = ['EcoMade', 'CoolMax', 'COOLMAX', 'iPhone', 'MicroMesh', 'BioGuard', 'PWXFLEX', 'McLaren']


def _split(tok):
    low = tok.lower()
    if len(tok) < 6 or low in WC or low in PROTECT or not re.fullmatch(r"[A-Za-z]+", tok):
        return tok
    parts = wordninja.split(tok)
    if len(parts) < 2:
        return tok
    if not all((len(p) >= 2 or p.lower() in ('a', 'i')) and p.lower() in WC for p in parts):
        return tok
    if any(p.lower() in ('ng', 'es', 'ar', 'cel', 'ed', 'er', 'ly', 's', 'ing', 'ion') for p in parts):
        return tok
    return ' '.join(parts)


def fix(t):
    if not t:
        return t
    t = re.sub(r"n’ ?t(?=[a-z])", "n’t ", t)
    t = re.sub(r"’ (t|s|re|ve|ll|d|m)\b", r"’\1", t)
    t = re.sub(r"([a-z][.,;:!?])([A-Za-z])", r"\1 \2", t)
    t = re.sub(r"([a-z])(2XU)", r"\1 \2", t)
    keep = {}
    for k, w in enumerate(CAMEL_KEEP):
        if w in t:
            keep['\x00%d\x00' % k] = w
            t = t.replace(w, '\x00%d\x00' % k)
    t = re.sub(r"([a-z])([A-Z][a-z])", r"\1 \2", t)
    t = re.sub(r"[A-Za-z]+", lambda m: _split(m.group(0)), t)
    for k, w in keep.items():
        t = t.replace(k, w)
    # ’ 在中文字型會顯示成全形，看起來像多一格空白，統一換成半形 '
    return re.sub(r" {2,}", " ", t).strip().replace("’", "'").replace("‘", "'")
