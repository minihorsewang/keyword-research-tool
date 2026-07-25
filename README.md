# 台灣 Google 印刷關鍵字查詢工具

輸入印刷相關種子關鍵字，從 Google Ads API 取得台灣搜尋資料，輸出 Excel 報告。也支援 Google Keyword Planner CSV 匯入分析。

## 專案狀態

```
V1.2 開發完成，等待 Google Basic Access 正式驗收
```

| 關卡 | 狀態 |
|------|------|
| 程式靜態驗收 | ✅ 通過 |
| 本機自動測試 62 項 | ✅ 通過 |
| Google Ads API Mock 驗收 | ✅ 通過 |
| Excel 輸出驗收 | ✅ 通過 |
| 正式 Google Ads API 實測 | ⏳ 等待 Basic Access 核准 |

## 使用方式

### 方法一：CSV 匯入（不需 API 權限）

```bash
python main.py
```

從 Google Keyword Planner 手動查詢 → 匯出 CSV → 放入 `input/` → 執行程式 → 取得分析 Excel。

### 方法二：Google Ads API 即時查詢（需 Basic Access）

```bash
python main.py --source google --keywords "貼紙印刷,標籤印刷" --customer-id 1234567890
```

或用文字檔輸入種子詞：

```bash
python main.py --source google
```

（需在 `input/keywords.txt` 每行放一個關鍵字）

## 測試

```bash
python tests/run_all.py
```

共 62 項測試，涵蓋 CSV 分析、關鍵字輸入、Client 初始化、結果對映、API Mock 查詢、Excel 輸出。

## 已確認通過的範圍

- CSV 匯入與清理（Big5、UTF-8、欄位辨識）
- 種子關鍵字輸入與去重（大小寫保留、數量/長度上限）
- Customer ID 驗證（去橫線、前導零保留、MCC 區分）
- Google Ads Client 載入（YAML 中文錯誤訊息）
- Google API 錯誤格式化（認證、授權、Basic Access、配額）
- API Mock 查詢與重試（指數退避）
- 月份、競爭程度、出價資料對映（enum 名稱安全轉換）
- DataFrame 轉換（種子詞來源、查詢資訊、月份補零、0 值保留）
- 最小版 Google Excel 報告輸出（查詢摘要 + Google 關鍵字結果）
- 查詢快取（Key 含 Customer ID / 地區 / 語言 / 網路）

## 等待最終驗收

Basic Access 核准後，執行：

```bash
python main.py --source google --keywords "貼紙印刷,標籤印刷" --customer-id 你的正式帳戶ID
```

確認項目：

- [ ] 有回傳 Google 建議關鍵字
- [ ] 地區為台灣
- [ ] 語言為中文
- [ ] 搜尋量不是全部空白
- [ ] 競爭程度與出價正常
- [ ] 月份資料正確
- [ ] 產生 `Google關鍵字查詢_日期時間.xlsx`
- [ ] Excel 只有「查詢摘要」與「Google 關鍵字結果」

## 目錄結構

```
keyword_research/
├─ main.py                      # 主程式（--source csv|google）
├─ requirements.txt
├─ google-ads.yaml              # 本機限定
├─ credentials.json             # 本機限定
├─ input/                       # CSV 或 keywords.txt
├─ output/                      # Excel 報告
├─ logs/
├─ cache/                       # API 查詢快取
├─ config/
│  ├─ categories.json
│  ├─ intent_rules.json
│  ├─ business_rules.json
│  ├─ column_aliases.json
│  ├─ override_rules.json
│  └─ google_query.json         # API 查詢條件
├─ src/
│  ├─ csv_loader.py
│  ├─ data_cleaner.py
│  ├─ classifier.py
│  ├─ scorer.py
│  ├─ keyword_cluster.py
│  ├─ page_planner.py
│  ├─ excel_exporter.py
│  ├─ override.py
│  ├─ utils.py
│  ├─ keyword_input.py
│  ├─ google_ads_client.py
│  ├─ keyword_query.py
│  ├─ google_result_mapper.py
│  └─ query_cache.py
├─ tests/
│  ├─ run_all.py
│  ├─ data/
│  ├─ test_google_ads_client.py
│  ├─ test_google_excel_output.py
│  ├─ test_google_result_mapper.py
│  ├─ test_keyword_input.py
│  └─ test_keyword_query_mock.py
└─ tools/
   ├─ generate_refresh_token.py
   └─ test_google_ads_connection.py
```

## Google Ads API 設定

### 本機敏感檔案

```text
credentials.json
google-ads.yaml
```

### google-ads.yaml 格式

```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_OAUTH_CLIENT_ID"
client_secret: "YOUR_OAUTH_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_10_DIGIT_MCC_ID"
use_proto_plus: true
```

注意：Customer ID 不寫在 `google-ads.yaml`，改放 `config/google_query.json`。

### 產生 Refresh Token

```bash
python tools/generate_refresh_token.py
```

### 測試連線

```bash
python tools/test_google_ads_connection.py
```

## Basic Access 申請

- 案件編號：`4-5126000041166`
- 狀態：等待 Google 審核
- 用途：台灣印刷與包裝產業內部關鍵字研究

## 安全注意事項

以下檔案不可提交到 GitHub，已列入 `.gitignore`：

- `credentials.json`
- `google-ads.yaml`
- `*Refresh Token*.txt`
- `cache/`

---

最後更新：2026-07-25
版本：V1.2
