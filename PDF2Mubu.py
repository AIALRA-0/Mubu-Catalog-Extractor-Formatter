import os
import fitz  # PyMuPDF

def escape_mubu_text(text):
    # 对text进行URL编码，以符合_mubu_text字段的格式
    return text.replace(" ", "%20").replace("：", "%EF%BC%9A").replace("(", "%28").replace(")", "%29")

def save_pdf_outline_to_opml(pdf_path, include_page_numbers, max_level, include_heading):  
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 提取目录（书签/大纲）
    outline = pdf_document.get_toc()  # 返回一个列表，每个条目是一个目录项
    
    if not outline:
        print("该PDF文档没有目录。")
        return
    
    # 获取第一级目录项并将其内容放入title中
    first_level_title = outline[0][1] if outline[0][0] == 1 else "PDF Document"
    
    # 使用first_level_title作为输出文件名
    output_opml_path = f"{first_level_title}.opml"  # 输出为 title.opml
    
    # 用于跟踪当前目录层级
    current_level = 0
    
    # 打开一个opml文件来写入目录
    with open(output_opml_path, "w", encoding="utf-8") as opml_file:
        # 写入OPML头部，并将第一级的内容放在<title>标签中
        opml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        opml_file.write('<opml version="2.0">\n')
        opml_file.write('  <head>\n')
        # 直接写入原始标题内容
        opml_file.write(f'    <title>{first_level_title}</title>\n')
        opml_file.write('  </head>\n')
        opml_file.write('  <body>\n')
        
        # 写入目录内容，跳过第一级内容
        for item in outline:
            level, title, page = item
            
            # 跳过第一级，因为它已经被用作标题
            if level == 1:
                continue
            
            # 如果超过最大层级，不再输出该项
            if level - 1 > max_level:
                continue
            
            # 如果选择包括页码，添加 (Page X)，否则只输出标题
            if include_page_numbers:
                text_to_display = f"{title} (Page {page})"
            else:
                text_to_display = title
            
            mubu_text = escape_mubu_text(text_to_display)
            
            # 添加heading属性，最多支持3个层级
            heading_attr = f' _heading="{level - 1}"' if include_heading and level - 1 <= 3 else ''
            
            # 如果当前层级比前一个大，表示进入了一个新的嵌套层级
            if level > current_level + 1:
                indent = "  " * current_level  # 用当前层级的缩进
            # 如果当前层级比前一个小或相同，结束之前的标签
            elif level <= current_level + 1:
                while current_level >= level - 1:
                    current_level -= 1
                    indent = "  " * current_level
                    opml_file.write(f'{indent}</outline>\n')
                    
            # 写入当前的目录项，包含可选的heading属性
            indent = "  " * (level - 2)  # 调整缩进，使第二级成为第一级
            opml_file.write(f'{indent}<outline text="{text_to_display}" _mubu_text="%3Cspan%3E{mubu_text}%3C/span%3E" _note="" _mubu_note=""{heading_attr}>\n')
            
            # 更新当前层级
            current_level = level - 1
        
        # 根据层级补齐关闭标签
        while current_level > 0:
            indent = "  " * (current_level - 1)
            opml_file.write(f'{indent}</outline>\n')
            current_level -= 1
        
        # 结束OPML文件
        opml_file.write('  </body>\n')
        opml_file.write('</opml>\n')

    print(f"PDF目录已保存到 {output_opml_path}")

# 输入PDF文件路径
while True:
    pdf_path = input("请输入PDF文件的绝对路径（支持拖拽）：").strip().strip('"').strip("'")

    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print("文件不存在，请检查路径是否正确。")
        continue

    # 检查是否为有效的PDF文件
    try:
        fitz.open(pdf_path)
        print("文件有效，开始处理...")
        break
    except Exception as e:
        print(f"无效的PDF文件：{e}")
        continue
print("*默认选项请直接回车")

# 询问用户是否要包含页码
include_page_numbers_input = input("是否包含页码？(Y/N，默认N): ").lower().strip()
include_page_numbers = include_page_numbers_input == 'y'

# 询问用户最高目录层级
max_level_input = input("请输入最高目录层级（最高输出的目录层级，从1开始，默认999）：").strip()
if max_level_input.isdigit() and int(max_level_input) > 0:
    max_level = int(max_level_input)
else:
    max_level = 999;

# 询问用户是否需要标题层级格式化
include_heading_input = input("是否进行标题层级格式化（最高支持H3）？(Y/N，默认Y): ").lower().strip()
# 除非明确输入 'n'，都将默认启用标题层级格式化
include_heading = include_heading_input != 'n'


# 保存PDF目录到默认的index.opml文件
save_pdf_outline_to_opml(pdf_path, include_page_numbers, max_level, include_heading)
