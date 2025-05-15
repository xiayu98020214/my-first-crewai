import webbrowser
from dotenv import load_dotenv
import gradio as gr
#from my_first_crewai.crew import MyFirstCrewai
from my_first_crewai.my_flow import GuideCreatorFlow
from my_first_crewai.tools.markdown_pdf import markdown_to_pdf
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
    response = my_flow.kickoff(inputs={"input_text": message})
    response = str(response)
    # response = "xiayu" + str(count)
    # count += 1
    return response

def go_to_amap():
    source = my_flow.state.guide_outline.source_ll
    destination = my_flow.state.guide_outline.destination_ll
    print("source:",source)
    print("destination",destination)
    url = f"https://uri.amap.com/navigation?from={source}&to={destination}&mode=car"
    #url = "https://www.baidu.com/"
    return f'<a href="{url}" target="_blank">开始导航</a>'

def navigate_to_destination():
    source = my_flow.state.guide_outline.source_ll
    destination = my_flow.state.guide_outline.destination_ll
    print("source:",source)
    print("destination",destination)
    url = f"https://uri.amap.com/navigation?from={source}&to={destination}&mode=car"
    webbrowser.open(url)
    return 

def generate_file(content):
    # 创建一个临时文件
    gr.Warning("开始保存文件")
    input_file = r"/home/gpu/work/my_first_crewai/output/report.txt"
    output_file = r"/home/gpu/work/my_first_crewai/output/report.pdf"
    markdown_to_pdf(input_file, output_file)
    gr.Warning("保存文件结束")

    return output_file
# 创建 ChatInterface
with gr.Blocks() as demo:
    gr.Markdown("# 智能周边游")
    gr.Markdown("和大模型进行多轮对话。")
    
    chatbot = gr.ChatInterface(
        fn=chat_fn,
        examples=["下周一，我31岁有两个孩子，从深圳到东莞松山湖，自驾游2天", "你是谁", "讲个笑话"],
    )
    
    with gr.Row():

        # navigate_btn = gr.Button("开始导航", variant="primary")
        # navigate_btn.click(fn=navigate_to_destination)

        gr.HTML(go_to_amap())

    with gr.Blocks():
        generate_btn = gr.Button("生成文件")
        download_btn = gr.DownloadButton(label="下载文件")

        
        generate_btn.click(
            generate_file,
            outputs=download_btn
        )

# from crewai import LLM
# from crewai.utilities.events import EventHandler, LLMStreamChunkEvent

# EventHandler
# class MyEventHandler(EventHandler):
#     def on_llm_stream_chunk(self, event: LLMStreamChunkEvent):
#         # Process each chunk as it arrives
#         print(f"Received chunk: {event.chunk}")

# # Register the event handler
# from crewai.utilities.events import crewai_event_bus
# crewai_event_bus.register_handler(MyEventHandler())
if __name__ == "__main__":
      
    demo.launch(server_name="0.0.0.0", server_port=8880)