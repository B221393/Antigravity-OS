---
name: schedule-wallpaper
description: スケジュールをデスクトップ壁紙に自動反映する
homepage: file:///c:/Users/Yuto/Desktop/app/VECTIS_SYSTEM_FILES/CAREER/SCHEDULE.md
metadata: {"clawdbot":{"emoji":"🖼️","requires":{"bins":["python"],"python_packages":["pillow","watchdog"]}}}
---

# Schedule Wallpaper (スケジュール壁紙)

スケジュールファイルの変更を監視し、自動でデスクトップ壁紙を更新するスキル。

## 🔒 安全性

- **読み取り専用**: スケジュールファイルを読み取るだけで、変更しない
- **ローカルのみ**: ネットワーク通信なし
- **制限付き書き込み**: `c:\Users\Yuto\Desktop\SHUKATSU_WALLPAPER.png` のみに書き込み
- **Windows API使用**: `ctypes.windll.user32.SystemParametersInfoW` で壁紙を設定

## 📁 関連ファイル

| ファイル | 役割 |
|---|---|
| `CAREER/SCHEDULE.md` | スケジュール入力（ユーザーが編集） |
| `data/SCHEDULE.json` | 構造化スケジュールデータ |
| `bin/update_wallpaper.py` | 壁紙生成スクリプト |
| `bin/schedule_wallpaper_watcher.py` | ファイル監視デーモン |

## 🚀 使い方

### 手動更新（1回限り）

```bash
cd c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\bin
python update_wallpaper.py
```

### 自動監視モード（ファイル変更を検知）

```bash
cd c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\bin
python schedule_wallpaper_watcher.py
```

または、バッチファイルで起動:

```bash
START_WALLPAPER_WATCHER.bat
```

### Windows起動時に自動開始

スタートアップフォルダにショートカットを追加:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ScheduleWallpaperWatcher.lnk")
$Shortcut.TargetPath = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\bin\START_WALLPAPER_WATCHER.bat"
$Shortcut.WorkingDirectory = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\bin"
$Shortcut.WindowStyle = 7  # Minimized
$Shortcut.Save()
```

## 📝 スケジュールの書式

`SCHEDULE.md` 内のテーブル形式を解析:

```markdown
| 日付 | 曜日 | 予定 | ステータス |
| **2/3** | 月 | 面接 | 📋 予定 |
| **2/1** | 土 | ES提出 | ✅ 完了 |
```

## 🎨 壁紙デザイン

- **解像度**: 1920x1080
- **スタイル**: サイバーパンク風ダークテーマ
- **表示件数**: 最大5件の直近イベント
- **配置**: 右上にスケジュールパネル

## ⚙️ カスタマイズ

`bin/update_wallpaper.py` を編集:

- `width`, `height`: 壁紙サイズ
- `panel_x`, `panel_y`: パネル位置
- カラースキーム: `draw.rectangle`, `draw.text` の色指定
