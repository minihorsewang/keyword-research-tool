# 台灣 Google 印刷關鍵字查詢工具

本專案的核心目標，是讓使用者輸入一批印刷相關的種子關鍵字，直接查詢 Google Ads Keyword Planner 的台灣搜尋資料，並輸出 Excel 報告。

目前已完成：

- Google Keyword Planner CSV 匯入、整理與分析技術原型
- Google Cloud 專案與 Google Ads API 啟用
- OAuth 2.0 桌面應用程式設定
- Refresh Token 產生
- Google Ads Developer Token 設定
- `google-ads.yaml` 本機設定
- Google Ads API 身分驗證與可存取帳戶連線測試
- Google Ads API Basic Access 申請送出

目前尚未完成：

- `KeywordPlanIdeaService.GenerateKeywordIdeas` 正式查詢功能
- 台灣地區與中文語言條件串接
- Google API 結果轉換成 DataFrame
- Google API 結果接回現有 Excel 分析流程
- Basic Access 審核通過後的正式帳戶驗收

> **目前版本定位：V1.1 API 認證與申請階段完成，正在等待 Basic Access 審核並準備開發關鍵字查詢功能。**

---

## 最新進度

### Google Ads API 設定狀態

| 項目 | 狀態 | 說明 |
|---|---|---|
| Google Ads 經理帳戶（MCC） | 已完成 | 已建立 Keyword Research Manager |
| Google Cloud 專案 | 已完成 | 專案名稱：`keyword-research-tool` |
| Google Ads API | 已啟用 | 已在 Google Cloud 啟用 |
| OAuth 品牌與目標對象 | 已完成 | 外部應用程式，開發測試中 |
| OAuth 用戶端 | 已完成 | 類型：電腦版應用程式 |
| `credentials.json` | 已完成 | 僅保存在本機，不上傳 GitHub |
| Refresh Token | 已完成 | 已成功授權並取得 |
| Developer Token | 已完成 | 目前存取層級仍為測試帳戶 |
| `google-ads.yaml` | 已完成 | 已完成本機設定 |
| API 連線測試 | 已完成 | 已成功列出可存取的 Google Ads 帳戶 |
| Basic Access 申請 | 已送出 | 等待 Google 審核 |
| Basic Access 案件編號 | 已取得 | `4-5126000041166` |
| 正式帳戶關鍵字查詢 | 尚未完成 | 等待 Basic Access 核准並開發查詢程式 |

Google 已寄送確認信，表示已收到 Basic Access 申請。一般初步審查時間約為 5 個工作日，但 Google 可能要求補充資料。

---

## 核心使用流程

### 目前可用流程：手動匯入 CSV

```text
Google Keyword Planner 手動查詢
        ↓
匯出 CSV
        ↓
放入 input/ 資料夾
        ↓
執行 Python 程式
        ↓
整理、分類、評分並輸出 Excel
```

### 目前已完成的 Google Ads API 認證流程

```text
建立 Google Ads 經理帳戶
        ↓
取得 Developer Token
        ↓
建立 Google Cloud 專案
        ↓
啟用 Google Ads API
        ↓
建立 OAuth 電腦版應用程式
        ↓
下載 credentials.json
        ↓
產生 Refresh Token
        ↓
建立 google-ads.yaml
        ↓
執行連線測試
        ↓
成功列出可存取的 Google Ads 帳戶
        ↓
送出 Basic Access 申請
```

### 最終目標流程

```text
輸入種子關鍵字
例如：貼紙印刷、標籤印刷、彩盒印刷
        ↓
程式呼叫 Google Ads API
        ↓
限定台灣地區與中文語言
        ↓
取得 Google 建議關鍵字與搜尋數據
        ↓
整理、分類、評分
        ↓
輸出 Excel 查詢報告
```

---

## 目前版本使用方式：手動匯入 CSV

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 準備輸入資料

從 Google Keyword Planner 匯出 CSV，放入 `input/` 資料夾。

目前支援：

- UTF-8、UTF-8 BOM、Big5、CP950 編碼
- 逗號或 Tab 分隔
- 中英文欄位名稱
- 多個 CSV、TSV 或 TXT 檔案合併處理

### 3. 執行程式

```bash
python main.py
```

### 4. 查看報告

Excel 報告會輸出到 `output/` 資料夾。

檔名格式：

```text
印刷關鍵字分析_YYYYMMDD_HHMMSS.xlsx
```

---

## Google Ads API 本機認證設定

### 已建立的本機敏感檔案

```text
credentials.json
google-ads.yaml
```

這些檔案只能保存在本機，不可上傳公開 GitHub。

### `google-ads.yaml` 設定格式

```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_OAUTH_CLIENT_ID"
client_secret: "YOUR_OAUTH_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_10_DIGIT_MCC_ID"
use_proto_plus: true
```

注意：

- `login_customer_id` 必須是 10 位數 MCC ID
- 不可包含橫線
- 必須以字串形式保存
- 不可將真實 Token 寫入 README 或提交到 GitHub

### 產生 Refresh Token

```bash
python tools/generate_refresh_token.py
```

### 測試 Google Ads API 連線

```bash
python tools/test_google_ads_connection.py
```

成功時會顯示：

```text
連線成功，可以存取的 Google Ads 帳戶：
customers/XXXXXXXXXX
```

目前這項測試已成功完成。

---

## Basic Access 申請進度

已送出 Google Ads API Basic Access Application。

申請內容包括：

- 工具用途：台灣印刷與包裝產業的內部關鍵字研究
- 使用者：公司內部人員
- API 功能：Keyword Planning Services
- 廣告類型：Search
- 不建立或修改廣告活動
- 不使用 App Conversion Tracking 或 Remarketing API
- 不提供一般大眾或外部客戶使用
- 已上傳 Google Ads API 工具設計文件 PDF

案件編號：

```text
4-5126000041166
```

目前狀態：

```text
Google 已收到申請，等待審核
```

在 Basic Access 通過前，Developer Token 仍為測試帳戶存取權，無法對正式廣告帳戶執行完整的關鍵字查詢。

---

## 最終版本預計使用方式

完成 Google Ads API 關鍵字查詢後，預計支援兩種輸入方式。

### 方法一：讀取文字檔

在 `input/keywords.txt` 中，每行放一個種子關鍵字：

```text
貼紙印刷
標籤印刷
彩盒印刷
紙盒印刷
食品標籤
```

執行：

```bash
python main.py --source google
```

### 方法二：命令列直接輸入

```bash
python main.py --keywords "貼紙印刷,標籤印刷,彩盒印刷"
```

以上兩種 Google 查詢入口目前尚未完成。

---

## Google 查詢預計取得的資料

完成 Google Ads API 串接後，程式應取得：

- 種子關鍵字
- Google 建議關鍵字
- 平均每月搜尋量
- 競爭程度
- 競爭指數
- 頁首出價低標
- 頁首出價高標
- 最近月份搜尋量
- 三個月變化
- 年增率
- 查詢地區
- 查詢語言
- 查詢時間

預設查詢條件：

- 地區：台灣
- 語言：中文
- 搜尋網路：Google Search

---

## Excel 報告

### 核心工作表

| 工作表 | 說明 |
|---|---|
| 查詢摘要 | 查詢時間、種子詞數量、結果數量與查詢條件 |
| Google 關鍵字結果 | Google 回傳的完整關鍵字數據 |
| 高搜尋量關鍵字 | 依平均每月搜尋量排序 |
| 高交易機會關鍵字 | 依搜尋意圖、搜尋量與公司承接能力排序 |
| 月份搜尋趨勢 | 每個關鍵字的月份搜尋量 |
| 原始資料 | 完整保留 Google API 或 CSV 原始資料 |
| 執行紀錄 | 程式版本、輸入來源、警告與錯誤 |

### 可選的進階分析工作表

| 工作表 | 說明 |
|---|---|
| 關鍵字分群 | 依產品、材質或用途分組 |
| 可能無關 | 標記可能與印刷業務無關的詞 |
| 網站頁面規劃 | 提供產品頁、估價頁或文章頁建議 |

---

## 專案結構

### 目前結構

```text
keyword_research/
├─ main.py
├─ requirements.txt
├─ README.md
├─ credentials.json              # 本機限定，不可提交
├─ google-ads.yaml               # 本機限定，不可提交
├─ input/
├─ output/
├─ logs/
├─ tools/
│  ├─ generate_refresh_token.py
│  └─ test_google_ads_connection.py
├─ config/
│  ├─ categories.json
│  ├─ intent_rules.json
│  ├─ business_rules.json
│  └─ column_aliases.json
├─ src/
│  ├─ csv_loader.py
│  ├─ data_cleaner.py
│  ├─ classifier.py
│  ├─ scorer.py
│  ├─ keyword_cluster.py
│  ├─ page_planner.py
│  ├─ excel_exporter.py
│  └─ utils.py
└─ tests/
   ├─ test_runner.py
   └─ data/
```

### 下一階段預計新增

```text
keyword_research/
├─ google-ads.yaml.example
├─ input/
│  └─ keywords.txt
├─ config/
│  └─ google_query.json
└─ src/
   ├─ google_ads_client.py
   ├─ keyword_input.py
   ├─ keyword_query.py
   ├─ google_result_mapper.py
   └─ query_cache.py
```

---

## 目前已完成

### CSV 分析功能

- [x] CSV、TSV、TXT 輸入
- [x] UTF-8、Big5、CP950 編碼嘗試
- [x] 中英文欄位自動辨識
- [x] 多個輸入檔案合併
- [x] 關鍵字清理與標準化
- [x] 完全重複關鍵字移除
- [x] 高度相似關鍵字標記
- [x] 規則式產品、材質、用途與加工分類
- [x] 搜尋意圖初步判斷
- [x] 公司承接能力與毛利評分
- [x] 關鍵字分群初版
- [x] 網站頁面建議初版
- [x] Excel 報告輸出
- [x] 執行 Log 與基本錯誤處理

### Google Ads API 認證與申請

- [x] 安裝 `google-ads` Python 套件
- [x] 建立 Google Cloud 專案
- [x] 啟用 Google Ads API
- [x] 建立 OAuth 品牌設定
- [x] 設定 OAuth 目標對象
- [x] 建立 OAuth 電腦版應用程式
- [x] 下載並保存 `credentials.json`
- [x] 將測試帳號加入 OAuth 測試使用者
- [x] 產生 Refresh Token
- [x] 取得並設定 Developer Token
- [x] 建立 `google-ads.yaml`
- [x] 設定 MCC `login_customer_id`
- [x] 建立 API 連線測試程式
- [x] 成功列出可存取 Google Ads 帳戶
- [x] 撰寫並上傳 API 工具設計文件
- [x] 送出 Basic Access Application
- [x] 收到 Google 申請確認信
- [ ] Basic Access 審核通過

---

## 核心功能尚未完成

### 1. 種子關鍵字輸入

- [ ] 讀取 `input/keywords.txt`
- [ ] 支援命令列 `--keywords`
- [ ] 去除空白與重複詞
- [ ] 檢查至少有一個有效關鍵字
- [ ] 記錄每次查詢使用的種子詞

### 2. Google Ads API 關鍵字查詢

- [x] 安裝 `google-ads` Python 套件
- [x] 建立 OAuth 憑證流程
- [x] 設定 Developer Token
- [x] 設定 MCC Login Customer ID
- [x] 建立 `google-ads.yaml`
- [x] 完成身分驗證連線測試
- [ ] 設定正式 Google Ads Customer ID
- [ ] 呼叫 `KeywordPlanIdeaService.GenerateKeywordIdeas`
- [ ] 取得 Google 相關關鍵字建議
- [ ] 取得平均每月搜尋量
- [ ] 取得競爭程度與競爭指數
- [ ] 取得頁首出價低標與高標
- [ ] 取得月份歷史搜尋量

### 3. 台灣與中文查詢條件

- [ ] 台灣地區 Geo Target Constant
- [ ] 中文語言 Constant
- [ ] Google Search 網路設定
- [ ] 查詢條件寫入報告與 Log
- [ ] 防止誤查成全球或其他語言資料

### 4. Google 回傳資料轉換

- [ ] 將 Google API 回傳結果轉成 pandas DataFrame
- [ ] 統一欄位名稱與資料型別
- [ ] 金額由 micros 正確換算
- [ ] 競爭程度轉為中文
- [ ] 月份資料展開成獨立欄位
- [ ] 保留種子詞與建議詞的來源關係

### 5. API 錯誤與限制處理

- [ ] OAuth 或 Refresh Token 失效
- [ ] Developer Token 尚未核准
- [ ] Customer ID 錯誤
- [ ] API 配額或頻率限制
- [ ] 一次輸入過多關鍵字
- [ ] 查不到資料
- [ ] 自動重試與等待
- [ ] 查詢快取，避免重複消耗配額

### 6. 接回目前分析流程

- [ ] Google API 結果接入 `clean_data()`
- [ ] 接入分類與搜尋意圖判斷
- [ ] 接入商業機會評分
- [ ] 接入 Excel 匯出
- [ ] 可選擇只輸出 Google 原始查詢結果
- [ ] 可選擇啟用進階分類與網站規劃

---

## 目前程式仍需修正

### 資料正確性

- [ ] 「原始資料」工作表必須保留清理前的完整資料
- [ ] 空白資料與重複資料分開統計
- [ ] 多輸入檔案時完整記錄所有檔名
- [ ] 動態保留 Google 匯出的月份搜尋量欄位
- [ ] 改善逗號與 Tab 分隔符號判斷
- [ ] 改善編碼辨識與中文亂碼檢查

### 分類與評分

- [ ] 無關詞規則應優先於一般交易意圖
- [ ] 支援同一關鍵字命中多個屬性
- [ ] `exclude_words` 真正加入排除或降權
- [ ] 「少量」須對照產品是否支援少量
- [ ] 「急件」須對照產品是否支援急件
- [ ] 「是否承接」為 false 時應排除或大幅降權
- [ ] 頁首出價、三個月變化與年增率加入評分
- [ ] 修正目前評分上限與分數尺度
- [ ] 避免大量關鍵字同時取得 100 分

### 分群

- [ ] 主關鍵字改由搜尋量或機會分數決定
- [ ] 群組內保存全部關鍵字
- [ ] 群組優先級改用加權分數
- [ ] 支援貼紙、標籤、紙盒等近義詞合併
- [ ] 加入人工覆寫分類與分群機制

### 地區字詞

- [ ] 補充 `台東` 等地區名稱與變體
- [ ] 驗證所有台灣縣市名稱規則

### 測試

- [ ] 改用 pytest
- [ ] Big5 失敗時測試必須真正失敗
- [ ] 缺欄位或空檔未拋錯時測試必須失敗
- [ ] 增加 Tab 分隔測試
- [ ] 增加多 CSV 合併測試
- [ ] 增加 10,000 筆完整流程測試
- [ ] 測試 Excel 是否包含預期工作表
- [ ] 測試 Excel 檔案被開啟占用時的錯誤
- [ ] 使用真實 Google Keyword Planner CSV 驗收
- [ ] 增加 Google Ads API Mock 測試
- [ ] Basic Access 通過後執行正式帳戶查詢驗收

---

## 下一階段開發順序

### V1.2：Google Ads API 最小可用查詢

下一步優先完成：

```text
讀取 keywords.txt 或 --keywords
        ↓
清理與去重
        ↓
呼叫 GenerateKeywordIdeas
        ↓
限定台灣與中文
        ↓
取得關鍵字、搜尋量、競爭程度與出價
        ↓
輸出簡單 Excel
```

### V1.3：月份趨勢與查詢紀錄

加入：

- 月份搜尋量
- 三個月變化
- 年增率
- 查詢條件
- 查詢快取
- API 執行紀錄

### V1.4：接回進階分析

最後再接回：

- 印刷產品分類
- 搜尋意圖
- 商業機會評分
- 關鍵字分群
- 網站頁面建議

---

## 非目前核心範圍

以下功能不是目前優先開發項目：

- 網頁介面
- 客戶登入系統
- Search Console API
- AI API 自動分類
- 自動產生 SEO 文章
- 自動發布網站內容
- 自動建立或修改 Google Ads 廣告活動

---

## 執行測試

目前 CSV 測試方式：

```bash
python tests/test_runner.py
```

Google Ads API 認證測試：

```bash
python tools/test_google_ads_connection.py
```

後續預計改為：

```bash
pytest -v
```

---

## 安全注意事項

以下資料不可提交到公開 GitHub：

- `credentials.json`
- `google-ads.yaml`
- `client_secret*.json`
- `token.json`
- `.env`
- Refresh Token
- Developer Token
- OAuth Client Secret
- 真實 Google Ads Customer ID 設定檔
- 真實客戶資料

`.gitignore` 至少應包含：

```gitignore
credentials.json
client_secret*.json
google-ads.yaml
token.json
.env
*Refresh Token*.txt
```

應提供不含真實憑證的範例檔：

```text
google-ads.yaml.example
```

---

## 目前狀態摘要

```text
CSV 分析原型：已完成
Google Cloud / OAuth：已完成
Refresh Token：已完成
Developer Token：已完成
google-ads.yaml：已完成
API 身分驗證連線測試：已完成
Basic Access 申請：已送出
Basic Access 核准：等待中
正式關鍵字查詢程式：尚未完成
Google API → Excel 整合：尚未完成
```

最後更新：2026-07-25
