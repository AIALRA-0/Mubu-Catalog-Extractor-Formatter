import requests
from bs4 import BeautifulSoup
import os
import fitz  # PyMuPDF
from urllib.parse import quote

def escape_mubu_text(text):
    # 对所有字符进行URL编码，包括中文
    return quote(text, safe="")

def fetch_wechat_reader_outline(url):
    """从微信读书网页爬取目录，并提取书名"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 提取书名，位于<head>中的<title>
    book_title_element = soup.find("title")
    if book_title_element:
        book_title = book_title_element.get_text(strip=True).split("-")[0].strip()
    else:
        book_title = "未命名书籍"

    # 查找class为readerCatalog的div，不再限定style属性
    catalog_div = soup.find("div", {"class": "readerCatalog"})
    if not catalog_div:
        print("未找到目录，请确认网页内容。")
        exit

    outline_items = catalog_div.select("li.readerCatalog_list_item")
    outline = []
    
    for item in outline_items:
        # 提取目录标题
        title_element = item.select_one(".readerCatalog_list_item_title_text")
        if title_element:
            title = title_element.get_text(strip=True)
        else:
            title = "无标题"

        # 从 item 中获取层级信息，直接从 HTML 中查找 "readerCatalog_list_item_level_"
        level = 0
        item_html = str(item)  # 将 item 转为字符串形式
        if "readerCatalog_list_item_level_" in item_html:
            # 从字符串中提取层级数字
            start_index = item_html.index("readerCatalog_list_item_level_") + len("readerCatalog_list_item_level_")
            level = int(item_html[start_index])
    
        # 微信读书网页没有页码信息，暂定为 0
        page = 0
        outline.append((level, title, page))
    
    return outline, book_title


def save_outline_to_opml(outline, pdf_file_name, include_page_numbers, max_level, include_heading):
    # 初始化 first_level_title，使用 PDF 文件名作为默认标题
    pdf_file_name = os.path.basename(pdf_file_name)  # 使用文件名而不是完整路径

    # 查找一级标题，一级标题的层级为 1
    first_level_titles = [item for item in outline if item[0] == 1]
    
    # 如果只有一个一级标题，则使用该标题作为输出的OPML文件名，并将其作为 title 显示
    if len(first_level_titles) == 1:
        first_level_title = first_level_titles[0][1]
        outline = [item for item in outline if item[0] != 1]  # 移除一级标题
        single_title = True
    else:
        # 否则使用 PDF 文件名作为标题，并从一级标题开始计算 heading
        first_level_title = os.path.splitext(pdf_file_name)[0]
        single_title = False

    output_opml_path = f"{first_level_title}.opml"

    current_level = 0  # 当前目录层级

    with open(output_opml_path, "w", encoding="utf-8") as opml_file:
        opml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        opml_file.write('<opml version="2.0">\n')
        opml_file.write('  <head>\n')
        opml_file.write(f'    <title>{first_level_title}</title>\n')  # 确保这里只显示文件名或一级标题
        opml_file.write('  </head>\n')
        opml_file.write('  <body>\n')
    
        for item in outline:
            level, title, page = item  # 每个目录项包含 (层级, 标题, 页码)
            if single_title:
                level -= 1
            
            if level > max_level:
                    continue
    
            # 生成要显示的目录文本
            text_to_display = f"{title} (Page {page})" if include_page_numbers else title
            mubu_text = escape_mubu_text(text_to_display)

            # 从start_heading_level 开始进行 heading 格式化，最高到3级标题
            heading_attr = f' _heading="{level}"' if include_heading and level >= 1 and level <= 3 else ''  # 设置标题格式化
    
            # 处理层级间的关系并关闭不必要的 outline 标签
            if level > current_level + 1:
                while current_level < level - 1:
                    current_level += 1
                    indent = "  " * current_level
                    opml_file.write(f'{indent}<outline>\n')
            
            elif level <= current_level:
                while current_level >= level:
                    indent = "  " * current_level
                    opml_file.write(f'{indent}</outline>\n')
                    current_level -= 1
    
            # 按 HTML 层级进行缩进
            indent = "  " * (level - 1)
            opml_file.write(f'{indent}<outline text="{text_to_display}" _mubu_text="%3Cspan%3E{mubu_text}%3C/span%3E" _note="" _mubu_note=""{heading_attr}>\n')
            current_level = level
    
        # 关闭所有未结束的 outline 标签
        while current_level > 0:
            indent = "  " * current_level
            opml_file.write(f'{indent}</outline>\n')
            current_level -= 1
    
        opml_file.write('  </body>\n')
        opml_file.write('</opml>\n')
    
    print(f"目录已保存到 {output_opml_path}")



# 判断是否为PDF文件路径或微信读书网页链接
def is_wechat_reader_url(path):
    return path.startswith("https://yd.qq.com/web/reader/") || path.startswith("https://weread.qq.com/web/reader/")

# 主函数
while True:
    path = input("请输入PDF文件/微信读书网页的路径（支持拖拽）：").strip().strip('"').strip("'")

    if not os.path.exists(path) and not is_wechat_reader_url(path):
        print("文件不存在/不是有效的微信读书网页链接，请检查路径是否正确。")
        continue

    if is_wechat_reader_url(path):
        outline, path = fetch_wechat_reader_outline(path)
        include_page_numbers = False
        print("网页链接有效，开始处理...")
    else:
        pdf_document = fitz.open(path)
        outline = pdf_document.get_toc()
        print("PDF文件有效，开始处理...")

    break

if os.path.exists(path):
    include_page_numbers = input("是否包含页码？(Y/N，默认N): ").lower().strip() == 'y'

max_level = int(input("请输入最高目录层级（从1开始，默认999）：").strip() or 999)
include_heading = input("是否进行标题层级格式化（最高支持H3）？(Y/N，默认Y): ").lower().strip() != 'n'

save_outline_to_opml(outline, path, include_page_numbers, max_level, include_heading)
