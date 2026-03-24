# VECTIS Code Analyzer

PythonのAST（抽象構文木）解析を用いた、自作の静的解析ツールです。
SciTools Understandのような高価なツールを使わずに、コードの構造を可視化します。

## 機能

- **クラス図生成**: Mermaid.js形式 (`class_diagram.mmd`)
- **依存関係グラフ**: Mermaid.js形式 (`dependency_graph.mmd`)
- **コールグラフ**: Mermaid.js形式 (`call_graph.mmd`)
- **メトリクス計測**: 循環的複雑度、行数などを集計 (`metrics_report.md`)

## 使い方

1. `run_analysis.bat` を実行します。
2. 解析したいPythonプロジェクトのフォルダパスを入力（またはドラッグ＆ドロップ）します。
3. 解析対象フォルダ内に `_analysis_output` フォルダが作成され、レポートが出力されます。

## Antigravity (VS Code) での表示

出力された `.mmd` ファイルは、Mermaid Preview拡張機能などで図として閲覧できます。
Markdownレポート (`metrics_report.md`) はそのままプレビューしてください。
