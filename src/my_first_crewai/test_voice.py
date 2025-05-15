import gradio as gr

# 本地音频文件路径
audio_path = r"/home/gpu/work/test_ws_xf_tts_3.wav"  # 替换为你的音频文件路径



with gr.Blocks() as demo:
    gr.Markdown("# 音频播放示例")
    # 创建音频组件并指定本地文件路径
    audio_component = gr.Audio(
        value=audio_path,
        label="播放本地音频",
        type="filepath"  # 明确指定类型（可选，默认即为此值）
    )





if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8880)