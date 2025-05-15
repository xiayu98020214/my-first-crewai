from dotenv import load_dotenv
import gradio as gr
from my_first_crewai.crew import MyFirstCrewai
from my_first_crewai.my_flow import GuideCreatorFlow
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

# 创建 ChatInterface
demo = gr.ChatInterface(
    fn=chat_fn,
    title="智能周边游",
    description="和大模型进行多轮对话。",
    examples=["下周一，我31岁有两个孩子，从深圳到东莞松山湖，自驾游2天", "你是谁", "讲个笑话"]
)

if __name__ == "__main__":
      
    demo.launch(server_name="0.0.0.0", server_port=8880)