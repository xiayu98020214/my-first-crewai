import gradio as gr
from xf_tts import get_xf_tts_ws_wav

voice_options = [
    ("xiaoyan", "女声-讯飞小燕"),
    ("aisjiuxu", "男声-讯飞九旭"),
    ("xiaofeng", "男声-讯飞小峰"),
    ("xiaokun", "男声-讯飞小昆"),
    ("xiaomei", "女声-讯飞小美"),
    ("xiaoqi", "女声-讯飞小琪"),
    ("xiaolin", "女声-讯飞小琳"),
    ("xiaoyou", "童声-讯飞小悠"),
]

def tts_play(text, voice_name):
    import os
    appid = os.getenv("XF_TTS_APPID")
    apikey = os.getenv("XF_TTS_APIKEY")
    apisecret = os.getenv("XF_TTS_APISECRET")
    wav_bytes = get_xf_tts_ws_wav(text, appid, apikey, apisecret, voice_name=voice_name)
    return (wav_bytes, "audio/wav")

with gr.Blocks() as demo:
    text_input = gr.Textbox(label="输入要合成的文本")
    voice_select = gr.Dropdown(choices=[v[0] for v in voice_options], label="选择音色", value="xiaoyan")
    tts_btn = gr.Button("语音播报")
    audio_output = gr.Audio(label="播放", interactive=False)
    tts_btn.click(tts_play, inputs=[text_input, voice_select], outputs=audio_output)

if __name__ == "__main__":
    demo.launch()