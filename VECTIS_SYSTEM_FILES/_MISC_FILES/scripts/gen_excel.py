import pandas as pd
import numpy as np

# 正規分布データの生成
mu, sigma = 0, 1 # 平均0, 標準偏差1
data = np.random.normal(mu, sigma, 1000)

# データフレーム作成
df = pd.DataFrame(data, columns=['Normal_Distribution_Values'])

# Excelファイルとして保存
output_file = 'c:/Users/Yuto/Downloads/app/normal_distribution.xlsx'
df.to_excel(output_file, index=False)
print(f"File saved: {output_file}")
