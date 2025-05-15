import argparse
from datetime import datetime
import time
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def markdown_to_pdf(input_file, output_file):
    """将 Markdown 文件转换为 PDF 文件"""
    # 读取 Markdown 文件内容
    #input_file = r"/home/gpu/work/my_first_crewai/output/report.txt"
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    

    # 配置中文字体
    font_config = FontConfiguration()
    css = CSS(string='''
        @font-face {
            font-family: SimHei;
            src: local('SimHei');
        }
        body { font-family: 'SimHei', sans-serif; }
    ''', font_config=font_config)
    
    # 将 Markdown 转换为 HTML
    html_content = markdown.markdown(
        markdown_text,
        extensions=['extra', 'codehilite', 'toc'],
        extension_configs={
            'codehilite': {'linenums': False}
        }
    )
    
    # 添加基本的 HTML 结构
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Markdown 转换的 PDF</title>
        <style>
            body {{ font-family: SimHei, sans-serif; margin: 2cm; }}
            h1, h2, h3 {{ color: #333; }}
            pre {{ background-color: #f5f5f5; padding: 1em; border-radius: 4px; overflow-x: auto; }}
            code {{ font-family: Consolas, monospace; }}
            blockquote {{ border-left: 4px solid #ddd; padding-left: 1em; margin-left: 0; color: #666; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    '''
    
    # 生成 PDF
    HTML(string=html_content).write_pdf(
        output_file,
        stylesheets=[css],
        font_config=font_config
    )
    print(f"转换为 {output_file}")

def main():
    """主函数：解析命令行参数并执行转换"""
    # parser = argparse.ArgumentParser(description='将 Markdown 文件转换为 PDF')
    # parser.add_argument('input', help='输入的 Markdown 文件路径')
    # parser.add_argument('-o', '--output', help='输出的 PDF 文件路径', default=None)
    # args = parser.parse_args()
    
    # 确定输出文件名
    # if args.output:
    #     output_file = args.output
    # else:
    #     # 如果没有指定输出文件名，使用输入文件名并将扩展名改为 .pdf
    #     output_file = args.input.rsplit('.', 1)[0] + '.pdf'
#     markdown_text = """# 在线 MarkDown 编辑器

# ![](https://pandao.github.io/editor.md/images/logos/editormd-logo-180x180.png)"""
#     now = datetime.now()
#     file_name = "report" + str(now) + ".pdf"
#     output_file = r"/home/gpu/work/my_first_crewai/output/"+file_name
    start = time.time()
    input_file = r"/home/gpu/work/my_first_crewai/output/report.txt"
    output_file = r"/home/gpu/work/my_first_crewai/output/report.pdf"
    markdown_to_pdf(input_file, output_file)
    print("during:",time.time()-start)

if __name__ == "__main__":
    main()    