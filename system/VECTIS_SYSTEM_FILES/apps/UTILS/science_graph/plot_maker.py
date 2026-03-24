import matplotlib.pyplot as plt
import pandas as pd
import scienceplots
import sys
import os

# 論文用のスタイルを適用
# 'science' スタイルと 'no-latex'（LaTeXなしでも動くモード）を指定
try:
    plt.style.use(['science', 'no-latex', 'grid'])
except Exception as e:
    print(f"Warning: Could not use science style: {e}")
    plt.style.use('ggplot') # フォールバック

def create_paper_graph(file_path, x_col, y_col, output_name="result"):
    """
    CSVを読み込んで、論文クオリティのグラフを即出力する関数
    """
    # 1. データ読み込み
    if not os.path.exists(file_path):
        print(f"Error: File not found {file_path}")
        return

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. グラフ描画（サイズは論文の推奨サイズに自動調整される）
    fig, ax = plt.subplots()
    
    # プロット（Originっぽい見た目で）
    if x_col in df.columns and y_col in df.columns:
        ax.plot(df[x_col], df[y_col], label='Proposed Method', linestyle='-', marker='o')
        
        # 3. 装飾（ここを一度決めたら一生変えなくていい）
        ax.set_xlabel(f"{x_col}")      # 軸ラベル
        ax.set_ylabel(f"{y_col}")
        ax.legend(title='Legend')      # 凡例
        
        # 4. 保存（PDFとPNG両方出すと便利）
        # PDFはベクター形式なので拡大しても荒れない（OriginのEPS代わり）
        output_base = os.path.splitext(output_name)[0]
        plt.savefig(f'{output_base}.pdf', dpi=300)
        plt.savefig(f'{output_base}.png', dpi=300)
        
        print(f"グラフを生成しました: {output_base}.pdf / .png")
    else:
        print(f"Error: Columns {x_col} or {y_col} not found in CSV")
        print(f"Available columns: {df.columns.tolist()}")

if __name__ == "__main__":
    # テスト用
    if len(sys.argv) > 1:
        # 簡易CLI: python plot_maker.py data.csv time voltage result
        create_paper_graph(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "result")
    else:
        print("Usage: python plot_maker.py <csv_file> <x_col> <y_col> [output_name]")
