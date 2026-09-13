import os
from pathlib import Path

# 定义文件夹路径
template_path = "html_gm.txt"  # 模板文件路径（位于当前目录）
input_dir = Path("DT")          # 存放 .text 文件的文件夹
output_dir = Path("details")    # 输出 .html 文件的文件夹

# 创建输出文件夹（如果不存在）
output_dir.mkdir(exist_ok=True)

# 读取 HTML 模板
with open(template_path, "r", encoding="utf-8") as f:
    template_content = f.read()

# 遍历 DT 文件夹中的所有 .text 文件
for text_file in input_dir.glob("*.text"):
    # 读取 .text 文件内容
    with open(text_file, "r", encoding="utf-8") as f:
        text_content = f.read()

    # 替换模板中的 ****text**** 占位符
    html_content = template_content.replace("****text****", text_content)

    # 生成输出文件名：同名的 .html 文件
    output_file = output_dir / (text_file.stem + ".html")

    # 写入 HTML 文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已生成: {output_file}")