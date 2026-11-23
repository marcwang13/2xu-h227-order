# 2XU H2-27 正式訂貨（經銷線上訂貨＋Excel 訂單本）

照 DESCENTE 27FW 正式訂貨（DSTC，`dst-27fw-main-order`）架構複製：一張卡片＝一款（同款多色列在同一張），性別／大類／系列（Story）篩選，尺寸格填數量，下單總覽，Excel 訂單本（含款式圖、實體圖）匯出／匯入，Apps Script 收單。交接規則看 DSTC repo 的 `ORDER_SYSTEMS_HANDOFF.md`（唯一正本）。

- 經銷商下單截止：2026/11/26（四）
- 原廠每色最少 20 件是全台灣合計（艾盟仕彙整後計），網站與 Excel 不寫
- 價格：台灣建議售價（訂單表 NTD MSRP）
- 到貨：只顯示 Drop 1／2／3，不放月份、不顯示「ETA X月」，也不顯示國外日期（Marc 11/23）

## 檔案

| 檔案 | 說明 |
|---|---|
| `index.html` | 前台（單一檔）。由 DSTC 範本經 `tools/adapt_from_dstc.py` 改成 2XU 版 |
| `config.js` | `SUBMIT_URL` 留空＝傳單模式（經銷商下載 Excel 訂單本傳給業務）。2XU 要另開新的試算表＋Apps Script，部署後把網址貼這裡 |
| `data.js` | `window.SDR_ITEMS`，一筆＝一個款色（503 筆／149 款） |
| `imgs.js` | 款式圖縮圖（110px，載入失敗時備援） |
| `rp.js` | 型錄照：`X2_RP` 圖檔寬高、`X2_RPI` 款色→型錄照、`X2_RPB` 沒有自己顏色照片的款色借同款 |
| `big/` | 款式圖（原廠訂單表內嵌圖，`<md5前12>.jpg`）與型錄照（`cp_p<頁>_<xref>.jpg`，PDF 原檔 JPEG 不重壓） |
| `logo.png` | EMERS-WHL TW 金色 logo |
| `apps-script/Code.gs` | 收單程式（由 DSTC 版改品牌字串、色、Drop 欄、NT$） |
| `tools/build_data.py` | 從原廠訂單表＋型錄 PDF 重產 `data.js`、`imgs.js`、`rp.js`、`big/`、`tools/match/*` |
| `tools/photo_override.json` | 型錄照片沒有色碼標籤時，目視後人工指定款色（key＝`p<頁>_<xref>`） |
| `tools/fix_text.py` | 型錄英文說明黏字補空格 |
| `tools/match/` | 比對紀錄：`match.csv`（每款色用哪張圖）、`unmatched_items.csv`（沒有自己型錄照／款式圖借同款）、`catalogue_photos_unused.csv`（型錄照片沒用上的原因）、`stats.json` |

原始檔放 `sources/`（不進 git）：`2XU_H2-27_order_form.xlsx`（原廠訂單表）、`2XU_H2-27_catalogue.pdf`（型錄）。

## 重產資料

```
pip install --break-system-packages pymupdf openpyxl pillow wordninja
rm -f big/*; python3 -W ignore tools/build_data.py
python3 -m http.server 8812   # 本機預覽 http://localhost:8812/
```

## 圖片規則

- 款式圖＝原廠訂單表「圖片」欄的圖，依圖片錨點列對到款色。原廠沒附這色的圖，或兩色貼同一張圖時，借同款其他顏色，標「款式圖為同款 X 供參考，顏色不同」（卡片備註、Excel 備註）。
- 實體圖＝型錄照片。依照片右上角色碼標籤＋照片下方款號自動對；沒標籤的單色商品照目視後寫進 `photo_override.json`。漸層底圖／跨格遮罩不算照片；長邊不到 220px 的照片（不比款式圖清楚）不用。
- 沒有自己顏色型錄照的款色，借同款其他顏色的型錄照，標「同款實體圖」。

## 跟 DSTC 不同的地方

- 網頁顯示台灣建議售價與零售金額（NT$），沒有韓幣、沒有「台灣定價待定」
- 分頁＝原廠 Story（13 個）；大類只有上身／下身／配件（袖套、小腿套歸配件）
- 尺寸依原廠訂單表各色開放尺寸，每款一組；加長版（XST～XXLT）排在一般尺寸後面另起一行
- 沒有過往參考（ref.js）、單色裁切（pc.js）
- 卡片主標題是英文品名，旁邊中文類別；標籤顯示新款／延續款、Activity、Drop
- Excel 訂單本欄位：Story、Drop、新款／延續、Activity、產地、建議售價(NT$)、零售金額(NT$)
- Apps Script「月份」欄改「Drop」，金額改 NT$
