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
- UTF-8 / UTF-8 BOM / Big5 編碼
- 逗號或 Tab 分隔
- 中英文欄位名稱

### 3. 執行程式

```bash
python main.py
```

### 4. 查看報告

Excel 報告會輸出到 `output/` 資料夾，檔名格式：`印刷關鍵字分析_YYYYMMDD_HHMMSS.xlsx`

## 輸出 Excel 包含

| 工作表 | 說明 |
|--------|------|
| 分析摘要 | 統計數據總覽 |
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
│  └─ column_aliases.json  # 欄位別名對照
├─ src/                    # 原始碼模組
│  ├─ csv_loader.py        # CSV 讀取與欄位辨識
│  ├─ data_cleaner.py      # 資料清理與去重
│  ├─ classifier.py        # 分類與意圖判斷
│  ├─ scorer.py            # 機會分數計算
│  ├─ keyword_cluster.py   # 關鍵字分群
│  ├─ page_planner.py      # 網站頁面建議
│  ├─ excel_exporter.py    # Excel 匯出
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

## 第一版範圍

包含：
- [x] CSV 讀取（UTF-8 / Big5）
- [x] 欄位自動辨識
- [x] 資料清理與標準化
- [x] 規則式分類（產品/材質/用途/加工）
- [x] 搜尋意圖判斷
- [x] 機會分數計算
- [x] 關鍵字分群
- [x] 網站頁面建議
- [x] Excel 報告輸出
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
