# 1. 加载需要的包（如果未安装 readxl，请先运行 install.packages("readxl")）
library(dplyr)
library(tidyr)
library(readxl)  # 必须加载此包来正确读取 .xlsx 文件

# 2. 读取两个文件
# f1 是 CSV 文件，保持 read.csv 即可
f1 <- read.csv("D:/硕士/MiREA/核对完的MiREA数据/各疾病富集结果/CD.csv", stringsAsFactors = FALSE)
# f2 是 Excel 文件，必须使用 read_excel
f2 <- read_excel("D:/硕士/MiREA/核对完的MiREA数据/cd/pdsp_jaccard_overlap_vectorized.xlsx")

# 3. 展开富集结果中的基因列，并去除可能存在的隐形空格
f1_expanded <- f1 %>%
  # 使用 separate_rows 直接将 "APC/CCL5/CD2" 拆分为多行
  separate_rows(Genes, sep = "/") %>%
  # 安全起见，去除基因名两端可能存在的隐形空格
  mutate(Genes = trimws(Genes))

# 4. 去重：如果一个基因对应多个细胞，只保留 P_value 最小（最显著）的那个
f1_best <- f1_expanded %>%
  arrange(P_value) %>%
  distinct(Genes, .keep_all = TRUE)

# 5. 准备用于映射的参考字典（将列名重命名为 GENE，方便后面匹配）
f1_to_merge <- f1_best %>%
  select(GENE = Genes, immune_mapped = Cell, p_mapped = P_value)

# 6. 映射到 f2 
# 同样对 f2 的 GENE 列清除一下隐形空格，确保 100% 匹配成功
f2_cleaned <- f2 %>%
  mutate(GENE = trimws(GENE))

result <- f2_cleaned %>%
  left_join(f1_to_merge, by = "GENE") %>%
  # 将匹配到的结果覆盖或赋值到 immune 和 p 列
  mutate(immune = immune_mapped,
         p = p_mapped) %>%
  # 移除合并带来的中间列
  select(-immune_mapped, -p_mapped)

# 7. 导出最终合并好的文件
output_path <- "D:/硕士/MiREA/核对完的MiREA数据/cd/cddata.csv"
write.csv(result, output_path, row.names = FALSE)

# 动态打印正确的保存路径
cat("映射完成！文件已成功保存为：\n", output_path, "\n")