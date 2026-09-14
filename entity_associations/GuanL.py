import pandas as pd
import math
import argparse
import os

# 创建参数解析器
parser = argparse.ArgumentParser(description='读取基因-微生物关联文件')
parser.add_argument('-f', '--file', type=str, required=True, help='文件名前缀，如 gc 表示读取 gcGuanL.txt')
parser.add_argument('-d', '--directory', type=str, default='.', help='文件所在目录，默认为当前目录')

args = parser.parse_args()

# 构建完整文件路径
filename = f"{args.file}GuanL.txt"  # gc + GuanL.txt = gcGuanL.txt
filepath = os.path.join(args.directory, filename)

# 创建 gcGL1 和 gcGL2 文件夹（如果不存在）
folder1 = os.path.join(args.directory, f"{args.file}GL1")
folder2 = os.path.join(args.directory, f"{args.file}GL2")

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

print(f"已创建/确认文件夹: {folder1}")
print(f"已创建/确认文件夹: {folder2}")

# 定义列名（根据实际情况修改）
column_names = ['Column1', 'Column2', 'Column3', 'Column4','Column5','Column6','Column7','Column8','Column9']

# 读取文件
df = pd.read_csv(filepath, sep='\t', names=column_names)

column_values1 = df['Column1']
column_values2 = df['Column2']
column_values3 = df['Column3']
column_values4 = df['Column4']
column_values5 = df['Column5']
column_values6 = df['Column6']
column_values7 = df['Column7']
column_values8 = df['Column8']
column_values9 = df['Column9']
i=0
for i in range(len(df)):
    import sys
    import time
    a = i + 1
    f = open(folder1 + "/" + str(a) + ".txt", "w+")
    sys.stdout = f
    gene = column_values2[i]
    micro = column_values3[i]
    meta = column_values6[i]
    imm = column_values7[i]
    if gene != '@':
        print('{ id: "',gene,'", name: "',gene,'", category: "Gene" },')
    if micro != '@':
        print('{ id: "',micro,'", name: "',micro,'", category: "Microbiota" },')
    if meta != '@':
        print('{ id: "',meta,'", name: "',meta,'", category: "Metabolite" },')
    if imm != '@':
        print('{ id: "',imm,'", name: "',imm,'", category: "Immune_cell" },',)
    for j in range(len(df)):
        if gene != '@':
            if column_values2[j] == gene:
                if column_values3[j] != '@':
                    print('{ id: "',column_values3[j],'", name: "',column_values3[j],'", category: "Microbiota" },')
                if column_values6[j] != '@':
                    print('{ id: "',column_values6[j],'", name: "',column_values6[j],'", category: "Metabolite" },')
                if column_values7[j] != '@':
                    print('{ id: "',column_values7[j],'", name: "',column_values7[j],'", category: "Immune_cell" },')
        if micro != '@':
            if column_values3[j] == micro:
                if column_values2[j] != '@':
                    print('{ id: "',column_values2[j],'", name: "',column_values2[j],'", category: "Gene" },')
                if column_values6[j] != '@':
                    print('{ id: "',column_values6[j],'", name: "',column_values6[j],'", category: "Metabolite" },')
                if column_values7[j] != '@':
                    print('{ id: "',column_values7[j],'", name: "',column_values7[j],'", category: "Immune_cell" },',)
        if meta != '@':
            if column_values6[j] == meta:
                if column_values2[j] != '@':           
                    print('{ id: "',column_values2[j],'", name: "',column_values2[j],'", category: "Gene" },')
                if column_values3[j] != '@':
                    print('{ id: "',column_values3[j],'", name: "',column_values3[j],'", category: "Microbiota" },')
                if column_values7[j] != '@':
                    print('{ id: "',column_values7[j],'", name: "',column_values7[j],'", category: "Immune_cell" },',)
        if imm != '@':
            if column_values7[j] == imm:
                if column_values2[j] != '@':
                    print('{ id: "',column_values2[j],'", name: "',column_values2[j],'", category: "Gene" },')
                if column_values3[j] != '@':
                    print('{ id: "',column_values3[j],'", name: "',column_values3[j],'", category: "Microbiota" },')
                if column_values6[j] != '@':
                    print('{ id: "',column_values6[j],'", name: "',column_values6[j],'", category: "Metabolite" },')

for i in range(len(df)):
    import sys
    import time
    a = i + 1
    f = open(folder2 + "/" + str(a) + ".txt", "w+")
    sys.stdout = f
    print("    ],")
    print("links: [")
    gene = column_values2[i]
    micro = column_values3[i]
    meta = column_values6[i]
    imm = column_values7[i]
    for j in range(len(df)):
        if gene != '@':
            if column_values2[j] == gene:
                if column_values3[j] != '@' and float(column_values5[j]) > 0.01:
                    print('{ source: "',column_values3[j],'", target: "',column_values2[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 1 }, },')
                if column_values3[j] != '@' and float(column_values5[j]) <= 0.01:
                    print('{ source: "',column_values3[j],'", target: "',column_values2[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 2 }, },')
                if column_values6[j] != '@':
                    print('{ source: "',column_values2[j],'", target: "',column_values6[j],'", label: "Relates to", name: "',column_values9[j],'", lineStyle: { width: 1, color: "darkred" }, symbol: ["none", "arrow"], symbolSize: 10 },')
                if column_values7[j] != '@' and float(column_values8[j]) > 0.01:
                    print('{ source: "',column_values2[j],'", target: "',column_values7[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 1 }, },')
                if column_values7[j] != '@' and float(column_values8[j]) <= 0.01:    
                    print('{ source: "',column_values2[j],'", target: "',column_values7[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 2 }, },')
        if  micro != '@':
            if column_values3[j] == micro:
                if column_values2[j] != '@' and column_values2[j] != gene and float(column_values5[j]) > 0.01:
                    print('{ source: "',column_values3[j],'", target: "',column_values2[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 1 }, },')
                if column_values2[j] != '@' and column_values2[j] != gene and float(column_values5[j]) <= 0.01:
                    print('{ source: "',column_values3[j],'", target: "',column_values2[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 2 }, },')
                if column_values6[j] != '@':
                    print('{ source: "',column_values3[j],'", target: "',column_values6[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 1 }, },')
        if  meta != '@':
            if column_values6[j] == meta:
                if column_values2[j] != '@' and column_values2[j] != gene:
                    print('{ source: "',column_values2[j],'", target: "',column_values6[j],'", label: "Relates to", name: "',column_values9[j],'", lineStyle: { width: 1, color: "darkred" }, symbol: ["none", "arrow"], symbolSize: 10 },')
                if column_values3[j] != '@' and column_values3[j] != micro:
                    print('{ source: "',column_values3[j],'", target: "',column_values6[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 1 }, },')
        if imm != '@':
            if column_values7[j] == imm:
                if column_values2[j] != '@' and column_values2[j] != gene and float(column_values8[j]) > 0.01:
                    print('{ source: "',column_values2[j],'", target: "',column_values7[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 1 }, },')
                if column_values2[j] != '@' and column_values2[j] != gene and float(column_values8[j]) <= 0.01:
                    print('{ source: "',column_values2[j],'", target: "',column_values7[j],'", label: "Connected to", symbolSize: 10, lineStyle: { width: 2 }, },')
    print("    ]")
    print("};")
    print("var chart = echarts.init(document.getElementById('entity-relationship-chart",a,"'));")

print(a)
for i in range(10):
    meta = column_values6[i]
    if meta != '@':
        print(meta)