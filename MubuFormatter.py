import re
import os
import xml.etree.ElementTree as ET
from urllib.parse import quote

def remove_formatting(mubu_text, preserve_formatting):
    if not preserve_formatting:
        # 使用正则表达式去掉所有 %20class=%22xxxx%22 格式的编码
        mubu_text = re.sub(r'%20class=%22.*?%22', '', mubu_text)
    return mubu_text

def process_special_formatting(text):
    """对带有冒号（: 或 ：）的内容进行处理，加粗冒号前面的部分并进行正确编码"""
    # 匹配带有:或者：的行
    match = re.match(r'(.+?)([:：])(.+)', text)
    if match:
        # 提取冒号前、冒号和冒号后的部分
        before_colon, colon, after_colon = match.groups()
        
        # 根据给定的编码格式，加粗冒号前的部分
        before_colon_encoded = "%3Cspan%20class=%22bold%22%3E" + quote(before_colon) + "%3C/span%3E"
        
        # 冒号以及冒号后的部分也进行编码
        after_colon_encoded = "%3Cspan%3E" + quote(colon + after_colon) + "%3C/span%3E"
        
        # 返回合并后的编码字符串
        return before_colon_encoded + after_colon_encoded
    return "%3Cspan%3E" + quote(text) + "%3C/span%3E"
    
def add_heading_to_opml(opml_path, preserve_formatting, enable_detection):
    # 解析现有的OPML文件
    tree = ET.parse(opml_path)
    root = tree.getroot()

    # 遍历<outline>节点，按层级添加heading属性，并移除_mubu_text中的格式
    def process_outline(outline, level=1):
        # 获取 _mubu_text
        mubu_text = outline.get('_mubu_text', '')
        text_content = outline.get('text', '')

        # 删除编码中的格式
        cleaned_mubu_text = remove_formatting(mubu_text, preserve_formatting)

        # 如果启用了特殊格式检测，且文本中包含 ":" 或 "：" 则处理特殊格式
        if enable_detection and (':' in text_content or '：' in text_content):
            cleaned_mubu_text = process_special_formatting(text_content)
            outline.set('_mubu_text', cleaned_mubu_text)
            # 不设置 heading 属性
        else:
            # 添加 heading 属性，最多支持 3 个层级
            if level <= 3:
                outline.set('_heading', str(level))

        # 更新 _mubu_text 的内容
        outline.set('_mubu_text', cleaned_mubu_text)

        # 递归处理子节点
        for child in outline.findall('outline'):
            process_outline(child, level + 1)

    # 处理OPML文件中的所有<outline>节点
    for outline in root.findall('body/outline'):
        process_outline(outline)

    # 将结果保存回同一个文件
    tree.write(opml_path, encoding="UTF-8", xml_declaration=True)
    print(f"已更新OPML文件：{opml_path}")
   

# 输入OPML文件路径
while True:
    opml_path = input("请输入OPML文件的绝对路径（支持拖拽）：").strip().strip('"').strip("'")

    # 检查文件是否存在
    if not os.path.exists(opml_path):
        print("文件不存在，请检查路径是否正确。")
        continue

    # 检查是否为有效的OPML文件
    try:
        ET.parse(opml_path)
        print("文件有效，开始处理...")
        break
    except ET.ParseError as e:
        print(f"无效的OPML文件：{e}")
        continue

print("*默认选项请直接回车")

# 询问用户是否保留格式
preserve_formatting_input = input("是否保留原来的格式（粗体、斜体等）？(Y/N，默认N): ").lower().strip()
preserve_formatting = preserve_formatting_input == 'y'

# 询问用户是否启用小标题检测
enable_detection_input = input("是否启用小标题检测（检测带有冒号的行）？(Y/N，默认Y): ").lower().strip()
enable_detection = enable_detection_input != 'n'

# 更新OPML文件
add_heading_to_opml(opml_path, preserve_formatting, enable_detection)
