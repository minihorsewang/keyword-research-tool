# keyword-research-tool — 台灣印刷關鍵字分析工具

從 Google Ads Keyword Planner 匯出的 CSV 自動分析印刷關鍵字，產出結構化的 Excel 分析報告。

## 目錄結構

```
keyword_research/
├─ main.py              # 主程式入口
├─ requirements.txt     # Python 相依套件
├─ AGENTS.md            # 本專案說明
├─ input/               # 放入 Keyword Planner CSV
├─ output/              # Excel 報告輸出
├─ logs/                # 執行紀錄
├─ config/              # JSON 設定檔（可手動修改）
│  ├─ categories.json
│  ├─ intent_rules.json
│  ├─ business_rules.json
│  └─ column_aliases.json
├─ src/                 # Python 模組
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
   └─ data/             # 測試用 CSV
```

## 開發習慣

- 使用 `python main.py` 執行分析
- 使用 `python tests/test_runner.py` 執行測試
- 設定檔在 `config/`，修改後不需重啟
- 第一版無 API 依賴，純本機執行

## 同步對照表

| 項目 | 位置 |
|------|------|
| GitHub 倉庫 | `minihorsewang/keyword-research-tool` |
| 本機路徑 | `competitor-analysis/keyword_research/` |
| Obsidian 筆記 | `知識庫/keyword-research-tool.md` |
| 技能目錄 | `~/.config/opencode/skills/project-init/SKILL.md` |

專案初始化完成於 2026-07-25
