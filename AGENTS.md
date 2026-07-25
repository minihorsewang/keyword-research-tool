# keyword-research-tool — 台灣印刷關鍵字分析工具

從 Google Ads Keyword Planner CSV 或 Google Ads API 自動分析印刷關鍵字，產出結構化的 Excel 分析報告。

## 目錄結構

```
keyword_research/
├─ main.py                    # 主程式入口（支援 --source csv|google）
├─ requirements.txt           # Python 相依套件
├─ google-ads.yaml            # Google Ads API 憑證（本機限定）
├─ credentials.json           # OAuth 憑證（本機限定）
├─ AGENTS.md
├─ input/                     # 放入 CSV 或 keywords.txt
├─ output/                    # Excel 報告輸出
├─ logs/                      # 執行紀錄
├─ cache/                     # API 查詢快取
├─ tools/
│  ├─ generate_refresh_token.py
│  └─ test_google_ads_connection.py
├─ config/
│  ├─ categories.json
│  ├─ intent_rules.json
│  ├─ business_rules.json
│  ├─ column_aliases.json
│  ├─ override_rules.json     # 人工覆寫（可選）
│  └─ google_query.json       # Google Ads API 查詢條件
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
│  ├─ keyword_input.py        # 種子關鍵字輸入
│  ├─ google_ads_client.py    # GoogleAdsClient 初始化
│  ├─ keyword_query.py        # GenerateKeywordIdeas 查詢
│  ├─ google_result_mapper.py # API 結果轉 DataFrame
│  └─ query_cache.py          # API 查詢快取
└─ tests/
   ├─ test_runner.py
   └─ data/
```

## 開發習慣

- `python main.py` — CSV 模式（預設）
- `python main.py --source google` — Google Ads API 模式
- `python main.py --source google --keywords "貼紙印刷,標籤印刷"` — CLI 指定種子詞
- `python tests/test_runner.py` — 執行測試
- 設定檔在 `config/`，修改後不需重啟

## 同步對照表

| 項目 | 位置 |
|------|------|
| GitHub 倉庫 | `minihorsewang/keyword-research-tool` |
| 本機路徑 | `competitor-analysis/keyword_research/` |
| Obsidian 筆記 | `知識庫/keyword-research-tool.md` |
| 技能目錄 | `~/.config/opencode/skills/project-init/SKILL.md` |

專案初始化完成於 2026-07-25
