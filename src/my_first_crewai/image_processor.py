# 文件: src/my_first_crewai/image_processor.py
from io import BytesIO
import base64
import os
from openai import OpenAI

def generate_image_description(image):
    """
    使用Qwen模型通过OpenAI兼容接口生成图片描述
    
    Args:
        image: PIL格式的图片对象
        
    Returns:
        str: 图片的文本描述
    """
    try:
        # 将图片转换为base64编码
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # 使用阿里云提供的OpenAI兼容接口
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # 打印调试信息
        print("API Key是否存在:", "是" if os.getenv("DASHSCOPE_API_KEY") else "否")
        
        # 调用支持图像能力的模型
        completion = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {"role": "system", "content": "你是一个擅长描述图片内容的助手。请用简洁的中文描述上传的图片内容，关注旅游和露营相关内容。"},
                {"role": "user", "content": [
                    {"type": "text", "text": "请描述这张图片的内容，包括图片中的场景、物体、人物等关键信息，重点关注与露营旅游相关的信息。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]}
            ],
            max_tokens=500
        )
        
        # 提取生成的描述
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"使用OpenAI兼容接口调用Qwen模型时出错: {str(e)}")
        
        # 如果调用失败，提供一个默认描述
        return "无法处理图片，将继续处理您的文字输入。"

def process_image_and_text(image, message, my_flow):
    """
    处理图片和文本输入，将图片描述与文本输入结合
    
    Args:
        image: PIL格式的图片对象，可能为None
        message: 用户输入的文本消息
        my_flow: 处理流程对象
        
    Returns:
        str: 处理后的响应文本
    """
    if image is not None:
        # 调用Qwen模型生成图片描述
        image_description = generate_image_description(image)
        
        # 打印图片描述，用于检查效果
        print("图片描述结果:", image_description)
        
        # 合并图片描述和用户文本输入
        combined_input = f"{message}\n图片描述：{image_description}"
    else:
        combined_input = message
    
    # 调用原有的流程处理
    response = my_flow.kickoff(inputs={"input_text": combined_input})
    response = str(response)
    return response