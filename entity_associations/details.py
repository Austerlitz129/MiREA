import numpy as np
import csv
import pandas as pd
import re
import os
import sys
import time
from Bio import Entrez, Medline
Entrez.email="***"

column_names = ['Column1', 'Column2', 'Column3']
df = pd.read_csv('Pmids.txt', sep='\t',names=column_names)
column_values1 = df['Column1']
column_values2 = df['Column2']
column_values3 = df['Column3']

column_names = ['Column1', 'Column2', 'Column3','Column4']
dl = pd.read_csv('detail.txt', sep='\t',names=column_names)
column1 = dl['Column1']
column2 = dl['Column2']
column3 = dl['Column3']
column4 = dl['Column4']

os.makedirs("./DT", exist_ok=True)
# 在文件开头获取命令行参数
# 运行方式: python detail.py -d "Helicobacter pylori-induced gastric cancer"
if len(sys.argv) > 2 and sys.argv[1] == '-d':
    d_value = sys.argv[2]
else:
    print("错误：必须指定参数 -d")
    print("使用方法：python detail.py -d 'your disease name'")
    sys.exit(1)  # 退出程序

for i in range(len(df)):
    f = open("./DT/" + str(column_values1[i]) + ".txt", "w+")
    sys.stdout = f
    for j in range(len(dl)):
        if column_values2[i] == column1[j] and column_values3[i] == column2[j]:
            pmid = str(column3[j])
            handle = Entrez.efetch(db='pubmed', id=pmid, rettype='medline', retmode='text',retmax=10000)
            medline_records = Medline.parse(handle)
            records = list(medline_records)
            for record in records:
                out1 = record["DP"]
                out2 = record["JT"]
                out3 = record["TI"]
                out4 = record["AU"]
                print(pmid,"\t",d_value,'\t',out1,"\t",out2,"\t",out3,"\t",out4,"\t",column4[j])
            break

with open("id.txt", encoding='utf-16') as f:
    rows = list(csv.reader(f))
ids = list([row[0] for row in rows[0:]])

column_names = ['Column1', 'Column2', 'Column3','Column4','Column5','Column6','Column7']
for id in ids:
    file_path = './DT/' + str(id) + '.txt'
    
    # 1. 检查文件是否真的存在
    if not os.path.exists(file_path):
        print(f"警告：文件 {file_path} 不存在，已跳过。")
        continue

    # 2. 读取文件
    # 2. 读取文件（添加 encoding 和 encoding_errors 参数）
    dtxt = pd.read_csv(file_path, sep='\t', names=column_names, encoding='utf-8', encoding_errors='ignore')
    
    # 3. 关键检查：判断读取到的数据表是不是空的！
    if dtxt.empty:
        print(f"警告：文件 {file_path} 是空的，没有数据，已跳过。")
        continue
        
    PMID = dtxt['Column1']
    DS = dtxt['Column2']
    DT = dtxt['Column3']
    JT = dtxt['Column4']
    TI = dtxt['Column5']
    AU = dtxt['Column6']
    EV = dtxt['Column7']
    
    # 同样抛弃 sys.stdout，改用标准的 with open 和 f.write
    html_file_path = "./DT/" + str(id) + '.text'
    with open(html_file_path, "w+", encoding='utf-8') as f:
        # 走到这里，说明文件里肯定有数据，索引 0 是绝对安全的！
        f.write(f"{PMID[0]}\n")
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('<tr>\n')
        f.write('<th>\n')
        f.write('Disease\n')
        f.write('</th>\n')
        f.write('<td>\n')
        f.write(f"{d_value}\n")
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('<tr>\n')
        f.write('<th>\n')
        f.write('Year\n')
        f.write('</th>\n')
        f.write('<td>\n')
        f.write(f"{DT[0]}\n")
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('<tr>\n')
        f.write('<th>\n')
        f.write('Journal\n')
        f.write('</th>\n')
        f.write('<td>\n')
        f.write(f"{JT[0]}\n")
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('<tr>\n')
        f.write('<th>\n')
        f.write('Title\n')
        f.write('</th>\n')
        f.write('<td>\n')
        f.write(f"{TI[0]}\n")
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('<tr>\n')
        f.write('<th>\n')
        f.write('Author\n')
        f.write('</th>\n')
        f.write('<td>\n')
        f.write(f"{AU[0]}\n")
        f.write('</td>\n')
        f.write('</tr>\n')
        f.write('<tr>\n')
        f.write('<th>\n')
        f.write('Evidence\n')
        f.write('</th>\n')
        f.write('<td>\n')
        f.write(f"{EV[0]}\n")





