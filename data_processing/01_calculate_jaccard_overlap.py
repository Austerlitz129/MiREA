import pandas as pd
import numpy as np

# 1. 读取数据
df = pd.read_excel("pdsp.xlsx", sheet_name="pdsp")

gene_col = "Standardization"
microbe_col = "Standardization.1"
pmid_col = "PMID"

# 提取并清理
df = df[[gene_col, microbe_col, pmid_col]].dropna(subset=[microbe_col])
df = df.drop_duplicates()

# 2. 分别统计基因和微生物的总文献数（Series格式）
gene_totals = df.groupby(gene_col)[pmid_col].nunique().rename('gene_total')
microbe_totals = df.groupby(microbe_col)[pmid_col].nunique().rename('microbe_total')

# 3. 统计交集 a
result_df = df.groupby([gene_col, microbe_col])[pmid_col].nunique().reset_index()
result_df.rename(columns={pmid_col: "a"}, inplace=True)

# 4. 将总数合并(Merge)到交集数据框中
result_df = result_df.merge(gene_totals, on=gene_col).merge(microbe_totals, on=microbe_col)

# 5. 向量化计算 b 和 c（直接列对列相减，无需循环）
result_df['b'] = result_df['gene_total'] - result_df['a']
result_df['c'] = result_df['microbe_total'] - result_df['a']

# 6. 向量化计算 Jaccard 和 Overlap
# Jaccard = a / (a + b + c)
result_df['Jaccard'] = result_df['a'] / (result_df['a'] + result_df['b'] + result_df['c'])

# Overlap = a / min(a+b, a+c)
# 使用 np.minimum 直接获取两列中对应行的最小值
min_ab_ac = np.minimum(result_df['a'] + result_df['b'], result_df['a'] + result_df['c'])
result_df['Overlap'] = result_df['a'] / min_ab_ac

# 7. 整理最终列名并按基因首字母排序
result_df.rename(columns={gene_col: 'GENE', microbe_col: 'Microbiota'}, inplace=True)
result_df = result_df[['GENE', 'Microbiota', 'a', 'b', 'c', 'Jaccard', 'Overlap']]
df_sorted = result_df.sort_values("GENE", key=lambda x: x.str.upper())

# 8. 导出结果
df_sorted.to_excel("pdsp_jaccard_overlap_vectorized.xlsx", index=False, engine='openpyxl')

print(f"向量化计算完成，共输出 {len(df_sorted)} 对关联！")
