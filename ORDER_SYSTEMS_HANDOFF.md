# 經銷線上訂貨系統：AI 交接文件

完整交接文件只維護一份正本，在 `marcwang13/dst-27fw-main-order` 的 [`ORDER_SYSTEMS_HANDOFF.md`](https://github.com/marcwang13/dst-27fw-main-order/blob/main/ORDER_SYSTEMS_HANDOFF.md)。本 repo（2XU H2-27）不另寫副本，改交接內容只改那一份。

## 本 repo 變更紀錄
- 2026-11-23 12:10（Grok Bot）：Marc 反映款式圖畫質差 → 款式圖改訂單表原檔不重壓；新增 2XU 官網同款同色高解析圖（`of.js`、`big/of_*.jpg`，136 款色：商品圖 59 款色 162 張、實穿照 91 款色 541 張），卡片／放大檢視多「商品圖」分頁；商品說明與功能點翻成繁中（`tools/zh/zh.json`）。細節見 README「畫質與官網圖」「中文說明」。

- 2026-11-23 13:40（Grok Bot）：收單開通準備（Marc 批准，比照 DSTC）：修正線上模式 Email 驗證列被註解吃掉而不顯示的 bug（adapt_from_dstc.py）；Code.gs 尺寸順序補 2XU 尺碼（M1/M2/L1/L2、XXXL、T 加長、OSFA）、加測試用指令碼屬性 NOTIFY_TO_TEST、安裝說明改系統帳號；交單折數 2XU 未確認、暫沿用 DSTC 5 折並在交單檔註記。開通步驟見 box /workspace/upl9/2xu_as/STEPS.md，config.js 仍空（傳單模式）。
- 2026-11-23 14:08（Grok Bot）：收單開通（Marc 批准，比照 DSTC）：系統帳號 emerswhlsystem.marc@gmail.com 新建試算表「2XU H2-27 正式訂貨 線上訂單」＋Apps Script 部署 v1，config.js 接 SUBMIT_URL；指令碼屬性未設 PREORDER_SSO_SECRET／ADMIN_KEY（同 WAAC，訂單彙整票券由 Early Buy 收單程式代驗）。後台 https://docs.google.com/spreadsheets/d/1uG5_S6ga0fLiHiL4U_5OB-zYVQyy_yQmaKRqTVMpJnc/edit
