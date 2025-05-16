from dotenv import load_dotenv
import gradio as gr
import os
from my_first_crewai.my_flow2 import kickoff3
from my_first_crewai.image_processor import generate_image_description
from my_first_crewai.my_flow import GuideCreatorFlow, summary_result
from my_first_crewai.tools.markdown_pdf import markdown_to_pdf
from PIL import Image
from my_first_crewai.xf_tts import get_xf_tts_ws_wav
from my_first_crewai.const import ENV_FILE, REPORT_PDF_FILE, REPORT_TXT_FILE
load_dotenv(ENV_FILE)



# Gradio 的 ChatInterface 只需传入一个函数
# 该函数参数为 message（用户输入），history（历史对话）
def chat_fn(message, history):
    # messages = []
    # for user, assistant in history:
    #     messages.append({"role": "user", "content": user})
    #     messages.append({"role": "assistant", "content": assistant})
    # messages.append({"role": "user", "content": message})
    
    if image_description != "":
        message = f"{message}\n图片描述：{image_description}"

    yield from kickoff3(message)

  





    
def generate_file(content):
    # 创建一个临时文件
    gr.Warning("开始保存文件")
    input_file = REPORT_TXT_FILE
    output_file = REPORT_PDF_FILE
    markdown_to_pdf(input_file, output_file)
    gr.Warning("保存文件结束")

    return output_file

image_description = ""
def process_image(image):
    global image_description

    image = Image.open(image)
    image_description = generate_image_description(image)

    print("image_description:",image_description)
    return f"图片描述：{image_description}"


# 创建 ChatInterface
with gr.Blocks(css="""
.logo-col {
    align-items: flex-start !important;
}
.logo-left img {
    margin-left: 0 !important;
    display: block;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    background: transparent !important;
}
.logo-left [class*="image-toolbar"] {
    display: none !important;
}
""") as demo:
    # Add logo at the top
    with gr.Row():
        with gr.Column(scale=0.2, elem_classes="logo-col"):
            gr.Image(
                r"/home/gpu/work/my_first_crewai/src/my_first_crewai/logo.jpg",
                show_label=False,
                width=100,
                elem_classes="logo-left"
            )
        with gr.Column():
            gr.Markdown("# 百鹿")
            gr.Markdown("### 您身边的露营推荐百晓生")
    
    with gr.Row():
        with gr.Column():
            chatbot = gr.ChatInterface(
                fn=chat_fn,
                examples=["下周一，我31岁有两个孩子，从深圳到东莞松山湖，自驾游2天", "我想去深圳类似图片中的场景中露营，帮我推荐一下", "我明天计划和朋友一起去类似图中这样的地方露营，帮我推荐一下"],
            )
            #audio_output = gr.Audio(label="语音回复", type="filepath", autoplay=True)

            with gr.Row():
                audio_path = os.path.join(os.path.dirname(__file__), "output", "test_ws_xf_tts_3.wav")
                audio_output = gr.Audio(label="语音回复", type="filepath", value=audio_path)
            
                with gr.Column():
                    generate_btn = gr.Button("生成报告文件")
                    download_btn = gr.DownloadButton(label="下载报告文件")
        
        generate_btn.click(
            generate_file,
            outputs=download_btn
        )

            
        
        with gr.Column():
            image_input = gr.Image(
                label="上传图片",
                type="filepath",
                image_mode="RGB",
                sources=["upload", "clipboard"],
                height=300,
                width=300,
                format="png"
            )
            
            image_input.change(
                fn=process_image,
                inputs=image_input,
                
            )
    




if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8880, allowed_paths=[os.path.dirname(__file__)])