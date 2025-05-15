from dotenv import load_dotenv
import gradio as gr
import os
from my_first_crewai.image_processor import generate_image_description
from my_first_crewai.my_flow import GuideCreatorFlow
from my_first_crewai.tools.markdown_pdf import markdown_to_pdf
from PIL import Image
load_dotenv("/home/gpu/work/my_first_crewai/.env")

#my_crew = MyFirstCrewai().crew()
my_flow = GuideCreatorFlow()
# 假设你有一个大模型的回复函数
def generate_response(messages):
    # messages: List[dict], 例如 [{"role": "user", "content": "你好"}]
    # 这里用简单回显模拟，实际应调用你的大模型
    last_user_message = messages[-1]["content"]
    return f"你说：{last_user_message}"


count = 1
# Gradio 的 ChatInterface 只需传入一个函数
# 该函数参数为 message（用户输入），history（历史对话）
def chat_fn(message, history):
    global count
    # history: List[Tuple[str, str]]，每个元素是 (user, assistant)
    # 构造大模型需要的 messages 格式
    messages = []
    for user, assistant in history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})
    # 调用大模型
    #response = my_crew.kickoff(inputs={'user_input': message})
    message = f"{message}\n图片描述：{image_description}"
    response = my_flow.kickoff(inputs={"input_text": message})
    response = str(response)
    # response = "xiayu" + str(count)
    # count += 1
    return response

def generate_file(content):
    # 创建一个临时文件
    gr.Warning("开始保存文件")
    input_file = r"/home/gpu/work/my_first_crewai/output/report.txt"
    output_file = r"/home/gpu/work/my_first_crewai/output/report.pdf"
    markdown_to_pdf(input_file, output_file)
    gr.Warning("保存文件结束")

    return output_file

image_description = ""
def process_image(image):
    global image_description
    # if image is None:
    #     return None, "请先上传图片"
    # try:
    #     # 创建保存图片的目录
    #     save_dir = "/home/gpu/work/my_first_crewai/output/images"
    #     os.makedirs(save_dir, exist_ok=True)
        
    #     # 生成唯一的文件名（使用时间戳）
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     filename = f"image_{timestamp}.png"
    #     save_path = os.path.join(save_dir, filename)
        
    #     # 保存图片
    #     with open(save_path, "wb") as f:
    #         f.write(open(image, "rb").read())
    image = Image.open(image)
    image_description = generate_image_description(image)

    print("image_description:",image_description)
    return image, f"图片描述：{image_description}"


# 创建 ChatInterface
with gr.Blocks() as demo:
    gr.Markdown("# 智能周边游")
    gr.Markdown("和大模型进行多轮对话。")
    
    with gr.Row():
        with gr.Column():
            chatbot = gr.ChatInterface(
                fn=chat_fn,
                examples=["下周一，我31岁有两个孩子，从深圳到东莞松山湖，自驾游2天", "你是谁", "我明天计划和朋友一起去类似图中这样的地方露营，帮我推荐一下"],
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
            image_output = gr.Image(label="预览图片", height=300, width=300)
            
            image_input.change(
                fn=process_image,
                inputs=image_input,
                outputs=[image_output, gr.Textbox(label="处理状态")]
            )
    
    with gr.Blocks():
        generate_btn = gr.Button("生成报告文件")
        download_btn = gr.DownloadButton(label="下载报告文件")
        
        generate_btn.click(
            generate_file,
            outputs=download_btn
        )



if __name__ == "__main__":
      
    demo.launch(server_name="0.0.0.0", server_port=8880)