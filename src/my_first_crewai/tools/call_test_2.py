import requests
import numpy as np


# FastAPI 服务地址（替换为你的服务器地址）
def call_wave2(text,file_path):
    url = "http://ry2.9gpu.com:43026/inference_zero_shot"
    zero_path = r'/home/gpu/work/my_first_crewai/src/my_first_crewai/tools/zero_shot_prompt.wav'
    # 准备请求数据
    files = {
        'prompt_wav': ('prompt.wav', open(zero_path, 'rb'), 'audio/wav')
    }
    data = {
        'tts_text': text,
        'prompt_text': '希望你以后能够做的比我还好呦。'
    }

    # 发送请求
    response = requests.post(url, files=files, data=data)

    # 保存音频
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"音频已保存为 {file_path}")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
    
if __name__ == "__main__":
    call_wave2("你好，我想去松山湖玩，你能和我一起吗？",r"/home/gpu/work/my_first_crewai/output/test_ws_xf_tts_3.wav")