# ==============================================================================
# 修改版：图4数据富集分析脚本（已修复多字节乱码及隐藏字符报错）
# ==============================================================================

# 1. 加载所有必须的包
library(clusterProfiler)
library(org.Hs.eg.db)
library(dplyr)
library(DOSE)

# 2. 读取背景文件并转换 ENTREZID
cat("正在读取背景库...\n")
gene2cell <- read.csv('D:/硕士/MiREA/图片/图们/图4数据/Cell_marker_Human.csv', header = TRUE, stringsAsFactors=FALSE)

gene2id <- bitr(unique(gene2cell$SYMBOL), 
                fromType="SYMBOL", 
                toType="ENTREZID",  
                OrgDb="org.Hs.eg.db") 

gene2cell_id <- merge(gene2cell, gene2id, by=intersect(names(gene2cell), names(gene2id)))

# 3. 导入你的目标基因
cat("正在读取你的真实基因列表...\n")
target_data <- read.csv("C:/Users/24164/Desktop/1.csv", header=TRUE, stringsAsFactors=FALSE)

# 请确保 target_data$ 后面紧跟的是你 csv 文件里的那一列的列名
gene_list_symbol <- target_data$GENE 

# ----------------------------------------------------------------------
# 【核心修复：乱码与隐形特殊字符强力清洗模块】
# ----------------------------------------------------------------------
# ① 强制转为 UTF-8 编码，遇到无法解析的异形多字节字符直接置空，防止 toupper 崩溃
gene_list_symbol <- iconv(gene_list_symbol, to = "UTF-8", sub = "")

# ② 暴力去污：只保留标准的英文字母、数字和连字符(-)，彻底抹除中文空格、回车等幽灵字符
gene_list_symbol <- gsub("[^a-zA-Z0-9-]", "", gene_list_symbol)

# ③ 剔除由于清洗可能产生的空行，防止后续富集报错
gene_list_symbol <- gene_list_symbol[gene_list_symbol != ""]
# ----------------------------------------------------------------------

# 内部名称清洗：自动修复潜在的 Excel 日期转换问题 (如 march 6, sept 9 等)
gene_list_symbol <- toupper(gene_list_symbol)
gene_list_symbol <- gsub("^MARCH\\s*6$", "MARCHF6", gene_list_symbol)
gene_list_symbol <- gsub("^MAR(\\d+)$", "MARCHF\\1", gene_list_symbol)
gene_list_symbol <- gsub("^SEPT\\s*9$", "SEPTIN9", gene_list_symbol)
gene_list_symbol <- gsub("^SEP(\\d+)$", "SEPTIN\\1", gene_list_symbol)

# 将输入的 SYMBOL 转成 ENTREZID 才能跑通原始富集
input_id <- bitr(unique(gene_list_symbol), fromType="SYMBOL", toType="ENTREZID", OrgDb="org.Hs.eg.db")
gene_list <- input_id$ENTREZID

# 4. 核心富集分析 (Bonferroni 和 BH 两次检验)
cat("正在进行富集分析计算...\n")
cancer_rich_bonferroni <- enricher(gene=gene_list,
                                   TERM2GENE = gene2cell_id[c('cell_id','ENTREZID')],
                                   TERM2NAME = gene2cell_id[c('cell_id','cell')],
                                   pvalueCutoff = 1,
                                   pAdjustMethod = 'bonferroni',
                                   qvalueCutoff = 1)

cancer_rich_benjamani <- enricher(gene=gene_list,
                                  TERM2GENE = gene2cell_id[c('cell_id','ENTREZID')],
                                  TERM2NAME = gene2cell_id[c('cell_id','cell')],
                                  pvalueCutoff = 1,
                                  pAdjustMethod = 'BH',
                                  qvalueCutoff = 1)

# 5. 合并与富集倍数计算
if(!is.null(cancer_rich_benjamani) && !is.null(cancer_rich_bonferroni)){
  
  cancer_rich_benjamani <- setReadable(cancer_rich_benjamani, OrgDb = org.Hs.eg.db, keyType="ENTREZID")
  cancer_rich_bonferroni <- setReadable(cancer_rich_bonferroni, OrgDb = org.Hs.eg.db, keyType="ENTREZID")
  
  cancer_rich_benjamani_df <- as.data.frame(cancer_rich_benjamani)
  cancer_rich_bonferroni_df <- as.data.frame(cancer_rich_bonferroni)
  
  names(cancer_rich_bonferroni_df)[names(cancer_rich_bonferroni_df) == 'p.adjust'] <- 'bonferroni'
  names(cancer_rich_benjamani_df)[names(cancer_rich_benjamani_df) == 'p.adjust'] <- 'Benjamini'
  
  cancer_rich <- merge(cancer_rich_bonferroni_df, cancer_rich_benjamani_df,
                       by=c("ID","Description","GeneRatio","BgRatio","pvalue","qvalue","geneID","Count"))
  
  cancer_rich <- cancer_rich[order(cancer_rich$pvalue),]
  
  enrichment_fold = apply(cancer_rich, 1, function(x){
    GeneRatio=eval(parse(text=x["GeneRatio"]))
    BgRatio=eval(parse(text=x["BgRatio"]))
    enrichment_fold=round(GeneRatio/BgRatio, 2)
    return(enrichment_fold)
  })
  cancer_rich$enrichment_fold <- enrichment_fold
  
  # 6. 最后提取模块：增加 enrichment_fold 和 Count
  final_result <- cancer_rich %>%
    dplyr::select(Genes = geneID, 
                  Cell = Description, 
                  P_value = pvalue,
                  enrichment_fold = enrichment_fold,
                  Count = Count) %>%
    dplyr::arrange(P_value)
  
  # 直接导出到工作文件夹中
  out_path <- "D:/硕士/MiREA/核对完的MiREA数据/各疾病富集结果/CD.csv"
  write.csv(final_result, out_path, row.names = FALSE)
  cat("\n【成功】原汁原味版富集完成！\n结果已保存为:", out_path, "\n")
  
} else {
  cat("\n【提示】未富集到任何显著结果，可能是输入的基因在背景库中均无对应细胞信息。\n")
}