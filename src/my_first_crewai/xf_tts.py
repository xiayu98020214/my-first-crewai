import time
import hashlib
import base64
import hmac
import json
import requests
from dotenv import load_dotenv
import websocket
import datetime
from urllib.parse import urlencode
import ssl
import threading
from pydub import AudioSegment
import io

load_dotenv("/home/gpu/work/my_first_crewai/.env")

def get_xf_tts(text, appid, apikey, apisecret, voice_name="xiaoyan", aue="lame", speed=50, volume=50, pitch=50):
    # 1. 构造鉴权参数
    host = "tts-api.xfyun.cn"
    url = f"https://{host}/v2/tts"
    cur_time = str(int(time.time()))
    param = {
        "aue": aue,  # lame=mp3, raw=pcm, speex-wb, speex
        "auf": "audio/L16;rate=16000",
        "voice_name": voice_name,
        "speed": str(speed),
        "volume": str(volume),
        "pitch": str(pitch),
        "engine_type": "intp65",
        "text_type": "text"
    }
    x_param = base64.b64encode(json.dumps(param).encode('utf-8')).decode('utf-8')
    x_checksum = hashlib.md5((apikey + cur_time + x_param).encode('utf-8')).hexdigest()
    headers = {
        "X-Appid": appid,
        "X-CurTime": cur_time,
        "X-Param": x_param,
        "X-CheckSum": x_checksum,
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }
    data = {
        "text": text
    }
    response = requests.post(url, headers=headers, data=data)
    # 2. 处理返回
    if response.headers["Content-Type"] == "audio/mpeg":
        return response.content  # mp3音频二进制
    else:
        print("TTS error:", response.text)
        return None
    

def get_xf_tts_ws(text, appid, apikey, apisecret, voice_name="xiaoyan"):
    """
    调用讯飞WebSocket TTS，返回PCM音频二进制
    """
    class Ws_Param(object):
        def __init__(self, APPID, APIKey, APISecret, Text):
            self.APPID = APPID
            self.APIKey = APIKey
            self.APISecret = APISecret
            self.Text = Text
            self.CommonArgs = {"app_id": self.APPID}
            self.BusinessArgs = {
                "aue": "raw",
                "auf": "audio/L16;rate=16000",
                "vcn": voice_name,
                "tte": "utf8"
            }
            self.Data = {
                "status": 2,
                "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")
            }

        def create_url(self):
            url = 'wss://tts-api.xfyun.cn/v2/tts'
            now = datetime.datetime.now()
            date = format_date_time(mktime(now.timetuple()))
            signature_origin = "host: " + "tts-api.xfyun.cn" + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
            signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                     digestmod=hashlib.sha256).digest()
            signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
            authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
            v = {
                "authorization": authorization,
                "date": date,
                "host": "tts-api.xfyun.cn"
            }
            url = url + '?' + urlencode(v)
            return url

    from wsgiref.handlers import format_date_time
    from time import mktime

    audio_chunks = []
    error_msg = {"msg": None}

    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            if code != 0:
                error_msg["msg"] = f"讯飞TTS错误: {message.get('message', '')} (code={code})"
                ws.close()
                return
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            audio_chunks.append(audio)
            status = message["data"]["status"]
            if status == 2:
                ws.close()
        except Exception as e:
            error_msg["msg"] = f"解析讯飞TTS返回数据异常: {e}"
            ws.close()

    def on_error(ws, error):
        error_msg["msg"] = f"WebSocket错误: {error}"

    def on_close(ws, close_status_code, close_msg):
        pass

    def on_open(ws):
        def run(*args):
            d = {
                "common": wsParam.CommonArgs,
                "business": wsParam.BusinessArgs,
                "data": wsParam.Data,
            }
            ws.send(json.dumps(d))
        threading.Thread(target=run).start()

    wsParam = Ws_Param(appid, apikey, apisecret, text)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open

    # 运行WebSocket，阻塞直到结束
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    if error_msg["msg"]:
        raise RuntimeError(error_msg["msg"])
    return b"".join(audio_chunks)  # 返回PCM音频二进制

def pcm_to_wav(pcm_bytes, sample_rate=16000, channels=1, sample_width=2):
    # sample_width=2 表示16bit
    audio = AudioSegment(
        data=pcm_bytes,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels
    )
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io.read()

def get_xf_tts_ws_wav(text, appid, apikey, apisecret, voice_name="xiaoyan"):
    """
    直接返回可播放的wav音频二进制
    """
    pcm_bytes = get_xf_tts_ws(text, appid, apikey, apisecret, voice_name=voice_name)
    wav_bytes = pcm_to_wav(pcm_bytes)
    return wav_bytes

if __name__ == "__main__":
    import os
    appid = os.getenv("XF_TTS_APPID")
    apikey = os.getenv("XF_TTS_APIKEY")
    apisecret = os.getenv("XF_TTS_APISECRET")
    text = "你好，我想去松山湖玩，你能和我一起吗？"
    wav_bytes = get_xf_tts_ws_wav(text, appid, apikey, apisecret, voice_name="xiaoyan")  # 女声
    with open("test_ws_xf_tts_3.wav", "wb") as f:
        f.write(wav_bytes)
    print("合成成功，已保存为 test_ws_xf_tts_3.wav")