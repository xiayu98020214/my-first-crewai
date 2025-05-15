import gradio as gr
from pathlib import Path

from my_first_crewai.tools.markdown_pdf import markdown_to_pdf

# def download_file():
#     file_path = "example.txt"  # 替换为实际的文件路径
#     return gr.DownloadButton(label="Download File", value=file_path)

# with gr.Blocks() as demo:
#     gr.Markdown("点击按钮下载文件。")
#     download_button = download_file()



def generate_file(content):
    # 创建一个临时文件
    input_file = r"/home/gpu/work/my_first_crewai/output/report.txt"
    output_file = r"/home/gpu/work/my_first_crewai/output/report.pdf"
    markdown_to_pdf(input_file, output_file)
    return output_file

with gr.Blocks() as demo:
    download_btn = gr.DownloadButton(label="下载文件")
    generate_btn = gr.Button("生成文件")
    
    generate_btn.click(
        generate_file,
        outputs=download_btn
    )

if __name__ == "__main__":
    demo.launch()