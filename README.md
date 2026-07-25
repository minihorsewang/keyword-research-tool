# 台灣印刷關鍵字分析工具

從 Google Ads Keyword Planner 匯出的 CSV 自動分析印刷關鍵字，產出結構化的 Excel 分析報告。

## 使用方式

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 準備輸入資料

從 Google Keyword Planner 匯出 CSV，放入 `input/` 資料夾。

支援格式：
- UTF-8 / UTF-8 BOM / Big5 / CP950 編碼（自動偵測 + 中文亂碼檢查）
- 逗號或 Tab 分隔（自動嗅探）
- 中英文欄位名稱
- 多個檔案可同時放入，會自動合併處理

### 3. 執行程式

```bash
python main.py
```

### 4. 查看報告

Excel 報告會輸出到 `output/` 資料夾，檔名格式：`印刷關鍵字分析_YYYYMMDD_HHMMSS.xlsx`

## 輸出 Excel 包含

| 工作表 | 說明 |
|--------|------|
| 分析摘要 | 統計數據總覽（原始/空白/重複/相似/有效） |
| 關鍵字總表 | 所有關鍵字完整資料與評分 |
| 高優先關鍵字 | 高優先級且非無關的關鍵字 |
| 關鍵字分群 | 按主題分組與建議頁面 |
| 網站頁面規劃 | 每個群組對應的頁面建議 |
| 可能無關 | 暫標為無關的關鍵字 |
| 原始資料 | 保留完整匯入資料 |
| 執行紀錄 | 執行時間與處理資訊 |

## 專案結構

```
keyword_research/
├─ main.py                 # 主程式入口
├─ requirements.txt        # Python 套件
├─ README.md               # 說明文件
├─ input/                  # 放入 CSV
├─ output/                 # Excel 報告輸出
├─ logs/                   # 執行紀錄
├─ config/                 # 可修改的設定檔
 │  ├─ categories.json      # 產品分類
 │  ├─ intent_rules.json    # 搜尋意圖規則
 │  ├─ business_rules.json  # 公司承接設定與評分
 │  ├─ column_aliases.json  # 欄位別名對照
 │  └─ override_rules.json  # 人工覆寫分類/分群（可選）
├─ src/                    # 原始碼模組
│  ├─ csv_loader.py        # CSV 讀取與欄位辨識
│  ├─ data_cleaner.py      # 資料清理與去重
│  ├─ classifier.py        # 分類與意圖判斷
│  ├─ scorer.py            # 機會分數計算
│  ├─ keyword_cluster.py   # 關鍵字分群
│  ├─ page_planner.py      # 網站頁面建議
 │  ├─ excel_exporter.py    # Excel 匯出
 │  ├─ override.py          # 人工覆寫載入與套用
 │  └─ utils.py             # 共用工具函式
└─ tests/
   ├─ test_runner.py       # 測試執行腳本
   └─ data/                # 測試用 CSV
```

## 執行測試

```bash
python tests/test_runner.py
```

## 設定檔說明

所有分類規則與公司設定皆在 `config/` 資料夾的 JSON 檔案中，可直接用記事本修改：

- **categories.json**：產品大類、材質、用途、加工分類關鍵字
- **intent_rules.json**：高交易意圖、資訊研究、可能無關的關鍵字
- **business_rules.json**：各產品承接能力、評分權重、加權與排除字詞
- **column_aliases.json**：CSV 欄位名稱對照表（中英文皆可）
- **override_rules.json**（可選）：人工覆寫分類與分群，格式見下方說明

## 人工覆寫機制

當自動分類或分群結果不正確時，可透過兩種方式強制指定：

### 方式一：JSON 設定檔

編輯 `config/override_rules.json`：

```json
{
  "classify": [
    {"keyword": "防水貼紙印刷", "產品大類": "貼紙印刷", "材質": "防水貼紙"}
  ],
  "cluster": [
    {"keyword": "貼紙印刷價格", "群組名稱": "貼紙估價"}
  ]
}
```

### 方式二：CSV 檔案

在 `input/` 資料夾放入 `override.csv`：

```csv
keyword,產品大類,材質,用途,加工,群組名稱
防水貼紙印刷,貼紙印刷,防水貼紙,,,
冷凍食品標籤印刷,,,冷凍食品標籤,,
貼紙印刷價格,,,,,貼紙估價
```

JSON 與 CSV 可同時存在，依關鍵字標準化後完全比對，兩者規則合併生效。

## 現有功能

包含：
- [x] CSV / TSV / TXT 讀取，自動編碼辨識（UTF-8 / Big5 / CP950）
- [x] 中英文欄位自動對應
- [x] 多檔案合併處理
- [x] 資料清理：空白移除、完全重複、高度相似標記
- [x] 規則式分類（產品大類 / 材質 / 用途 / 加工），支援多屬性命中
- [x] 搜尋意圖判斷（高交易意圖 / 資訊研究 / 可能無關），無關詞優先
- [x] 商業機會評分（搜尋量、競爭度、承接能力、毛利、意圖、出價、趨勢）
- [x] 固定分數尺度（跨報告不漂移）
- [x] exclude_words 降權、少量/急件對照產品支援性、「不承接」歸零
- [x] 關鍵字分群（主關鍵字由分數決定，加權優先級）
- [x] 網站頁面建議（Slug / H1 / CTA）
- [x] 人工覆寫分類與分群（JSON + CSV 雙通道）
- [x] Excel 報告輸出（8 個工作表）
- [x] 執行紀錄與錯誤處理

未包含：
- Google Ads API
- Search Console API
- AI API 串接
- 網頁介面
- 自動發布文章

## 擴充預留

程式架構已預留後續擴充點（介面層），後續可加入：
1. Google Ads API 自動取得搜尋量
2. Search Console API 分析排名機會
3. OpenAI / DeepSeek API 輔助分類
