# VECTIS Data Analyzer - 技術仕様書

## 概要

OriginLabライクなデータ分析・グラフ作成ツール。
シンプルなUIで、データ入力からグラフ生成までを直感的に行える。

---

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    VECTIS Data Analyzer                  │
├─────────────────────────────────────────────────────────┤
│  UI Layer (Tkinter)                                      │
│  ├── Header: タイトル、アクションボタン                   │
│  ├── Left Panel: データテーブル (Entry Grid)              │
│  └── Right Panel: グラフプレビュー (Matplotlib Canvas)    │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                              │
│  ├── self.data: 2D List (文字列)                         │
│  ├── CSV I/O: csv module                                 │
│  └── 数値変換: float()                                   │
├─────────────────────────────────────────────────────────┤
│  Graphing Engine                                         │
│  └── ★ Python Matplotlib (TkAgg Backend)                │
└─────────────────────────────────────────────────────────┘
```

---

## グラフエンジン

| 項目 | 内容 |
|------|------|
| **ライブラリ** | `matplotlib` |
| **バックエンド** | `TkAgg` (Tkinter統合) |
| **gnuplot** | 不使用 |

### 理由

- Tkinterとのネイティブ統合が容易
- 追加インストール不要（pipで完結）
- リアルタイムプレビューが可能
- 画像エクスポート機能あり

### 将来のオプション

- **gnuplot対応**: `subprocess`経由で`.gp`スクリプトを生成・実行
- **Plotly対応**: インタラクティブHTML出力

---

## ファイル構成

```
apps/UTILS/origin_clone/
├── app.py          # メインアプリケーション
├── SPEC.md         # この仕様書
└── (data/)         # ユーザーデータ保存用（将来）
```

---

## クラス構成

### `SimpleDataAnalyzer(tk.Tk)`

メインウィンドウ。

| メソッド | 説明 |
|----------|------|
| `setup_ui()` | UIレイアウト構築 |
| `select_column(col)` | X/Y軸の選択 |
| `load_sample_data()` | テストデータ挿入 |
| `open_csv()` | CSVファイル読み込み |
| `plot(type)` | グラフ描画（line/scatter） |

---

## 依存関係

```
tkinter      # 標準ライブラリ
matplotlib   # pip install matplotlib
```

---

## 今後の拡張案

1. データ統計表示（平均、標準偏差）
2. 複数データセット対応
3. グラフ画像のエクスポート
4. gnuplotバックエンド（オプション）
