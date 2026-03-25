# デスクトップ整理ガイド

## 目標構造

```
app/
├── projects/          # 開発プロジェクト
│   ├── Qumi_Core
│   ├── RUST_PROJECTS
│   ├── apps
│   ├── DYNAMIC_DESKTOP_PROJECT
│   ├── quake_sim
│   ├── quake_sim_3d
│   ├── agents
│   ├── personal
│   └── system
├── docs/              # ドキュメント
│   ├── README.md
│   ├── Integrated_System_Specs.md
│   ├── Integrated_Thinking_OS_Paper.md
│   ├── Todays_Tasks_from_Email.md
│   └── ai_collaboration_test.md
├── tools/             # ツール・スクリプト
│   ├── bin
│   ├── python_scripts
│   ├── check_calendar.py
│   ├── check_interview_schedule.py
│   ├── cleanup.py
│   ├── _agent
│   ├── _config
│   └── _launchers
├── temp/              # テンポラリ・プレビューファイル
│   ├── ai_comparison_index.html
│   ├── light_scatter_ai1_haiku.html
│   ├── light_scatter_ai2_optimized.html
│   ├── light_scatter_ai3_raycasting.html
│   ├── qumi_ui_concept.html
│   ├── gmail_out.txt
│   ├── tmp_objects.txt
│   └── large_tracked_files.txt
├── archive/           # 完了/廃止プロジェクト
│   └── archives
└── [Git・設定ファイル] # .git, .github, .gitignore, logs, docs, dashboard等
```

## 実行手順

### ステップ1: ディレクトリ作成
```bash
cd C:\Users\Yuto\Desktop\app
mkdir projects docs tools temp archive
```

### ステップ2: ファイル移動

**projects/ へ移動:**
```bash
move Qumi_Core projects\
move RUST_PROJECTS projects\
move apps projects\
move DYNAMIC_DESKTOP_PROJECT projects\
move quake_sim projects\
move quake_sim_3d projects\
move agents projects\
move personal projects\
move system projects\
```

**docs/ へ移動:**
```bash
move README.md docs\
move Integrated_System_Specs.md docs\
move Integrated_Thinking_OS_Paper.md docs\
move Todays_Tasks_from_Email.md docs\
move ai_collaboration_test.md docs\
```

**tools/ へ移動:**
```bash
move bin tools\
move python_scripts tools\
move check_calendar.py tools\
move check_interview_schedule.py tools\
move cleanup.py tools\
move _agent tools\
move _config tools\
move _launchers tools\
```

**temp/ へ移動:**
```bash
move ai_comparison_index.html temp\
move light_scatter_ai1_haiku.html temp\
move light_scatter_ai2_optimized.html temp\
move light_scatter_ai3_raycasting.html temp\
move qumi_ui_concept.html temp\
move gmail_out.txt temp\
move tmp_objects.txt temp\
move large_tracked_files.txt temp\
```

**archive/ へ移動:**
```bash
move archives archive\
```

### ステップ3: 検証
```bash
dir /B
```

完了後、以下の9つのディレクトリがルートに見えるはずです:
- projects/
- docs/
- tools/
- temp/
- archive/
- .git/
- logs/
- docs/ (既存、Git関連のドキュメント)
- dashboard/

## 注意事項
- `.git`, `.github`, `.gitignore*` などのGit関連ファイルは移動しない
- `logs/`, `docs/`, `dashboard/`, `.venv/` などの既存ディレクトリは保持
- 隠しファイル (`.` で始まる) は整理対象外
