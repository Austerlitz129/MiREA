import os
import re
import argparse

def parse_gcgl1_file(file_path):
    """解析gcGL1中的文件，提取nodes部分"""
    # 修复 3: 使用 utf-8-sig 完美去除 Windows 隐藏的 BOM 幽灵字符 (\ufeff)
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    nodes = []
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('//'):
            # 移除末尾的逗号，防止自带逗号导致重复
            line = line.rstrip(',')
            # 修复 2: 增强正则清洗，去除引号内首尾的空格 (" ACE " -> "ACE")
            line = re.sub(r'"\s*(.*?)\s*"', r'"\1"', line)
            nodes.append(line)
    
    return nodes

def parse_gcgl2_file(file_path):
    """解析gcGL2中的文件，提取links部分"""
    # 同理，使用 utf-8-sig
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    links = []
    # 匹配 links 数组中的内容
    links_match = re.search(r'links:\s*\[([\s\S]*?)\]\n\s*var chart', content)
    
    if not links_match:
        # 兼容备用方案：如果没有 var chart，直接尝试匹配 links:[...] 内部内容
        links_match = re.search(r'links:\s*\[([\s\S]*?)\]', content)
        
    if links_match:
        links_content = links_match.group(1)
        lines = links_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                line = line.rstrip(',')
                # 兼容性处理：有时连线末尾本身带了多余的逗号，如 width: 1 }, }，把它变干净
                line = line.replace('}, }', '} }').replace('},}', '}}')
                # 增强清洗空格
                line = re.sub(r'"\s*(.*?)\s*"', r'"\1"', line)
                if line:
                    links.append(line)
    
    return links

def merge_to_script(gcgl1_nodes, gcgl2_links, chart_id):
    """合并nodes和links生成完整的script.js文件"""
    
    # 修复 1: 关键点！这里必须用 ",\n" 来 join，确保每个 {} 之后都有换行和逗号
    nodes_part = ",\n".join(['        ' + node for node in gcgl1_nodes])
    if nodes_part:
        nodes_part += ","  # 给最后一个元素也加上逗号，与你的标准格式保持一致

    links_part = ",\n".join(['        ' + link for link in gcgl2_links])
    if links_part:
        links_part += ","

    # 以下是原封不动的 ECharts 模板配置
    script_content = f"""var data = {{
    nodes: [
{nodes_part}
    ],
    links: [
{links_part}
    ]
}};
var chart = echarts.init(document.getElementById('entity-relationship-chart{chart_id}'));
var categories = [
    {{ name: 'Microbiota', symbol: 'circle' }},
    {{ name: 'Gene', symbol: 'rect' }},
    {{ name: 'Metabolite', symbol: 'triangle' }},
    {{ name: 'Immune_cell', symbol: 'diamond' }}
];

// 配置项
var option = {{
    title: {{ text: '' }},
    tooltip: {{ trigger: 'item', formatter: '{{b}}' }},
    series: [
        {{
            type: 'graph',
            layout: "force",
            force: {{
                edgeLength: 30,
                repulsion: 400,
                gravity: 0.1,
            }},
            draggable: true,
            data: data.nodes,
            links: data.links,
            categories: categories,
            label: {{
                show: true,
                position: 'right',
                formatter: function (param) {{ return param.data.name || ''; }},
                fontSize: 12,
                fontWeight: 'bold',
            }},
            edgeSymbolSize: [10, 10],
            lineStyle: {{
                width: 1.5,
                curveness: 0,
                color: 'black',
            }},
            emphasis: {{ lineStyle: {{ width: 4 }} }},
            edgeLabel: {{
                show: true,
                formatter: function (param) {{ return param.data.name || ''; }},
                fontSize: 10,
                fontWeight: 'normal',
                distance: 10,
            }},
        }}
    ]
}};
chart.setOption(option);
"""
    return script_content

def process_folders(gcgl1_path, gcgl2_path, gcscript_path):
    """处理两个文件夹，合并生成script文件"""
    os.makedirs(gcscript_path, exist_ok=True)
    
    if not os.path.exists(gcgl1_path) or not os.path.exists(gcgl2_path):
        print("错误: gcGL1 或 gcGL2 文件夹不存在！")
        return
    
    files1 = [f for f in os.listdir(gcgl1_path) if f.endswith('.txt')]
    files2 = [f for f in os.listdir(gcgl2_path) if f.endswith('.txt')]
    
    common_names = set([os.path.splitext(f)[0] for f in files1]) & set([os.path.splitext(f)[0] for f in files2])
    
    print(f"找到 {len(common_names)} 个可匹配的文件。开始处理...")
    
    for name in sorted(common_names, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0):
        file1 = os.path.join(gcgl1_path, f"{name}.txt")
        file2 = os.path.join(gcgl2_path, f"{name}.txt")
        output_file = os.path.join(gcscript_path, f"{name}.script.js")
        
        try:
            nodes = parse_gcgl1_file(file1)
            links = parse_gcgl2_file(file2)
            
            # --- 孤立节点检查逻辑 ---
            node_ids = {re.search(r'id:\s*"([^"]+)"', n).group(1) for n in nodes if re.search(r'id:\s*"([^"]+)"', n)}
            linked_nodes = set()
            for l in links:
                src = re.search(r'source:\s*"([^"]+)"', l)
                tgt = re.search(r'target:\s*"([^"]+)"', l)
                if src: linked_nodes.add(src.group(1))
                if tgt: linked_nodes.add(tgt.group(1))
            
            orphan_nodes = node_ids - linked_nodes
            
            # 终端输出进度和警告
            if orphan_nodes:
                print(f"[{name}.txt] ⚠ 警告: 发现 {len(orphan_nodes)} 个孤立节点 {orphan_nodes}")
            else:
                print(f"[{name}.txt] ✔ 正常生成: {len(nodes)} 节点, {len(links)} 连线")

            # 清洗 ID 前后多余的空格，保证 HTML 容器挂载不出错
            chart_id_match = re.search(r'(\d+)', name)
            chart_id = chart_id_match.group(1) if chart_id_match else name.strip()
            
            script_content = merge_to_script(nodes, links, chart_id)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
                
        except Exception as e:
            print(f"[{name}.txt] ❌ 处理出错: {e}")
    
    print(f"\n完成！全部文件已输出到 {gcscript_path}")

def main():
    parser = argparse.ArgumentParser(description='合并gcGL1和gcGL2文件夹生成script.js文件')
    parser.add_argument('-g1', '--gcgl1', type=str, required=True, help='gcGL1文件夹路径')
    parser.add_argument('-g2', '--gcgl2', type=str, required=True, help='gcGL2文件夹路径')
    parser.add_argument('-o', '--output', type=str, default=None, help='输出文件夹路径（默认为gcscript）')
    
    args = parser.parse_args()
    gcscript_path = args.output if args.output else os.path.join(os.path.dirname(args.gcgl1), 'gcscript')
    
    process_folders(args.gcgl1, args.gcgl2, gcscript_path)

if __name__ == "__main__":
    main()
