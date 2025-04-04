# 项目简介
本项目包含两个幕布文档处理功能模块
- **目录提取**：从 `PDF/微信读书链接` 中提取目录并保存为支持幕布的 OPML 格式  
![image](https://github.com/user-attachments/assets/8e745cf4-a479-4567-9352-5593b7c91c22)
- **OPML 格式化**：格式化原有的幕布 OPML 格式文档  
![image](https://github.com/user-attachments/assets/4b1b2baa-976e-4dd2-9703-1c69a348e6fd)

## 目录提取模块
使用方式：运行 `MubuCatalogExtractor.py`  
此模块主要负责从 `PDF/微信读书链接` 中提取目录，并将目录内容格式化后保存为 OPML 文件格式，具体功能包括：
1. **目录提取**：提取 `PDF/微信读书链接` 文件中的目录（书签/大纲），并转换为 OPML 文件格式
2. **页码处理**：根据用户选择，决定是否包含页码信息在生成的 OPML 文件中
3. **层级限制**：用户可选最高的输出层级
3. **标题层级**：根据目录层级格式化标题，最多支持 3 层标题格式

## 目录格式化模块
使用方式：运行 `MubuCatalogFormatter.py`  
此功能的代码主要负责处理幕布导出的 OPML 文件的格式化，具体包括以下几点：
1. **格式保留或移除**：根据用户选择，决定是否保留原 OPML 文件中的格式（如粗体、斜体等）
2. **标题层级添加**：根据 OPML 文件内容，最多支持 3 级标题层级
3. **小标题检测**：如果启用小标题检测，脚本会检测包含冒号且非标题的内容并对其进行格式化，冒号前的内容会被加粗
![image](https://github.com/user-attachments/assets/088d3497-0672-4d55-ac82-e245d9f914ae)

## 如何运行
1. 安装项目依赖：
    ```bash
    pip install -r requirements.txt
    ```
2. 运行 目录提取 处理脚本：

    ```bash
    python MubuCatalogExtractor.py
    ```
3. 运行 目录格式化 处理脚本：

    ```bash
    python MubuCatalogFormatter.py
    ```
4. OPML导出：幕布-文档-导出/下载-OPML  
![image](https://github.com/user-attachments/assets/cc21bc2c-7a7f-4491-b3da-dcea9f29bdd3)
5. OPML导入：幕布-导入-导入OPML  
![image](https://github.com/user-attachments/assets/e5531089-48f4-4b34-8b42-a272b5762391)

## 注意事项
1. Latex支持：幕布导出OPML不带Latex格式，需要手动修复
