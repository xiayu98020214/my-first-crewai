import requests
import json
from typing import Optional, Any
import socket
import os
from datetime import datetime, timedelta
import locale
import re
from crewai.tools import BaseTool

class IPLocationTool(BaseTool):
    name: str = "IP地址查询工具"
    description: str = "获取当前IP地址和地理位置信息"

    def _run(self, _: Optional[str] = None) -> str:
        try:
            # 获取本机IP
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            # 从环境变量获取高德API密钥
            amap_key = os.getenv('AMAP_API_KEY')
            # 使用高德IP定位API
            url = f"https://restapi.amap.com/v3/ip?key={amap_key}&ip={ip}"
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == '1':
                return f"当前IP: {ip}\n位置: {data['province']}{data['city']}"
            else:
                return f"当前IP: {ip}\n无法获取详细位置信息"
        except Exception as e:
            return f"获取IP信息失败: {str(e)}"

class WeatherTool(BaseTool):
    name: str = "天气查询工具"
    description: str = (
        "获取指定城市的天气信息，包括当前天气和未来三天的天气预报。"
        "输入格式为城市名称，例如：'北京'、'上海'等。"
        "返回信息包括：温度、天气状况、湿度、风向、风力等。"
    )

    def _run(self, city: str) -> str:
        try:
            # 处理输入的城市名称
            if isinstance(city, str):
                # 如果输入是JSON字符串，尝试解析
                if city.startswith('{'):
                    try:
                        # 先处理Unicode转义序列
                        city = city.encode().decode('unicode_escape')
                        # 然后解析JSON
                        city_data = json.loads(city)
                        city = city_data.get('city', '')
                    except json.JSONDecodeError:
                        pass

            # 从环境变量获取心知天气API密钥
            seniverse_key = os.getenv('SENIVERSE_API_KEY')
            if not seniverse_key:
                return "错误：未找到心知天气API密钥，请检查.env文件中的SENIVERSE_API_KEY配置"

            # 获取当前天气
            now_url = f"https://api.seniverse.com/v3/weather/now.json?key={seniverse_key}&location={city}&language=zh-Hans&unit=c"
            now_response = requests.get(now_url)
            now_data = now_response.json()

            # 获取未来三天天气预报
            forecast_url = f"https://api.seniverse.com/v3/weather/daily.json?key={seniverse_key}&location={city}&language=zh-Hans&unit=c&start=0&days=4"
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()

            if 'status_code' in now_data or 'status_code' in forecast_data:
                return f"API错误：{now_data.get('status', '未知错误')}，错误代码：{now_data.get('status_code', '未知')}"

            # 处理当前天气数据
            if 'results' in now_data:
                now_weather = now_data['results'][0]['now']
                current_weather = (
                    f"{city}当前天气：\n"
                    f"天气：{now_weather.get('text', '未知')}\n"
                    f"温度：{now_weather.get('temperature', '未知')}°C\n"
                    f"体感温度：{now_weather.get('feels_like', '未知')}°C\n"
                    f"湿度：{now_weather.get('humidity', '未知')}%\n"
                    f"风向：{now_weather.get('wind_direction', '未知')}\n"
                    f"风力：{now_weather.get('wind_scale', '未知')}级\n"
                )
            else:
                current_weather = f"无法获取{city}的当前天气信息"

            # 处理未来三天天气预报数据
            if 'results' in forecast_data:
                forecast_weather = forecast_data['results'][0]['daily']
                forecast_info = f"\n{city}未来三天天气预报：\n"
                for day in forecast_weather[1:]:  # 跳过今天，只显示未来三天
                    forecast_info += (
                        f"\n{day.get('date', '未知')}：\n"
                        f"白天：{day.get('text_day', '未知')}，"
                        f"温度：{day.get('high', '未知')}°C\n"
                        f"夜间：{day.get('text_night', '未知')}，"
                        f"温度：{day.get('low', '未知')}°C\n"
                        f"降水概率：{day.get('precip', '0')}%\n"
                    )
            else:
                forecast_info = f"\n无法获取{city}的未来天气预报信息"

            return current_weather + forecast_info

        except Exception as e:
            return f"获取天气信息失败: {str(e)}"

class TrafficTool(BaseTool):
    name: str = "交通信息查询工具"
    description: str = "获取两个地点之间的交通信息，包括驾车、公交、步行等路线规划"

    def _run(self, query: str) -> str:
        try:
            # 处理输入格式
            if isinstance(query, str):
                # 如果输入是JSON字符串，尝试解析
                if query.startswith('{'):
                    try:
                        query_data = json.loads(query)
                        query = query_data.get('query', '')
                    except json.JSONDecodeError:
                        pass
                
                # 处理Unicode转义序列
                query = query.encode().decode('unicode_escape')
            
            # 解析查询参数
            try:
                # 支持两种格式：用空格分隔或直接连接
                if ' ' in query:
                    origin, destination, mode = query.split(' ')
                else:
                    # 尝试从字符串中提取信息
                    parts = query.replace('到', ' ').replace('自驾', ' ').split()
                    if len(parts) >= 2:
                        origin = parts[0]
                        destination = parts[1]
                        mode = '自驾'
                    else:
                        return "错误：无法解析输入格式，请使用'起点 终点 交通方式'格式"
            except ValueError:
                return "错误：输入格式应为'起点 终点 交通方式'，例如：'深圳 东莞松山湖 自驾'"
            
            # 从环境变量获取高德API密钥
            amap_key = os.getenv('AMAP_API_KEY')
            if not amap_key:
                return "错误：未找到高德API密钥，请检查.env文件中的AMAP_API_KEY配置"
            
            # 高德地图API
            url = f"https://restapi.amap.com/v3/direction/driving?key={amap_key}&origin={origin}&destination={destination}&extensions=all"
            
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == '1' and data['route']:
                route = data['route']
                path = route['paths'][0]
                
                return f"从{origin}到{destination}的驾车路线：\n" \
                       f"总距离：{int(path['distance'])/1000:.1f}公里\n" \
                       f"预计时间：{int(path['duration'])/60:.0f}分钟\n" \
                       f"过路费：{path.get('toll', '0')}元\n" \
                       f"路线：{path['steps'][0]['instruction']}"
            else:
                return f"无法获取交通信息，API返回：{data}"
        except Exception as e:
            return f"获取交通信息失败: {str(e)}"
        

class TimeTool(BaseTool):
    name: str = "时间查询工具"
    description: str = (
        "获取当前时间信息，包括日期、时间和星期几。"
        "支持以下功能：\n"
        "1. 获取当前时间（不传参数）\n"
        "2. 查询指定日期的星期几（格式：YYYY-MM-DD）\n"
        "3. 查询相对日期（如：下周六、下下周日等）\n"
        "4. 查询明天、后天等相对日期"
    )

    def _run(self, query: str = None) -> str:
        try:
            # 设置中文locale
            locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
            
            # 如果没有输入，返回当前时间
            if not query:
                now = datetime.now()
                return (
                    f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}\n"
                    f"星期：{['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][now.weekday()]}"
                )
            
            # 尝试解析为日期
            try:
                dt = datetime.strptime(query.strip(), "%Y-%m-%d")
                weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][dt.weekday()]
                return f"{query} 是 {weekday}"
            except ValueError:
                pass

            # 处理"明天"、"后天"等相对日期
            now = datetime.now()
            if query in ["明天", "后天", "大后天", "大大后天"]:
                days_map = {"明天": 1, "后天": 2, "大后天": 3, "大大后天": 4}
                target_date = now + timedelta(days=days_map[query])
                weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][target_date.weekday()]
                return (
                    f"{query}是 {target_date.strftime('%Y年%m月%d日')}，"
                    f"{weekday}"
                )

            # 尝试解析相对日期（如：下周六）
            match = re.match(r"^(这|下*)周([一二三四五六日天])$", query)
            if match:
                prefix = match.group(1)
                weekday_map = {"一":0,"二":1,"三":2,"四":3,"五":4,"六":5,"日":6,"天":6}
                target_weekday = weekday_map[match.group(2)]
                current_weekday = now.weekday()
                
                # 计算"下"的数量
                if prefix == "这":
                    weeks_ahead = 0
                else:
                    weeks_ahead = len(prefix)
                
                # 计算距离本周目标日的天数
                days_until = (target_weekday - current_weekday) % 7
                if prefix == "这":
                    # "这周X"：如果今天就是目标日，返回今天，否则返回本周内下一个目标日
                    target_date = now + timedelta(days=days_until)
                else:
                    # "下周X"：下一个目标日（不含本周），以此类推
                    if days_until == 0:
                        days_until = 7
                    days_until += 7 * (weeks_ahead - 1)
                    target_date = now + timedelta(days=days_until)
                
                return (
                    f"{query} 的日期是 {target_date.strftime('%Y-%m-%d')}，"
                    f"{['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][target_weekday]}"
                )
            
            return "请输入日期（YYYY-MM-DD）或如'下周六'、'明天'等，不输入则返回当前时间"
            
        except Exception as e:
            return f"获取时间信息失败: {str(e)}"

class ImageSearchTool(BaseTool):
    name: str = "图片搜索工具"
    description: str = (
        "使用提示词搜索网络图片。"
        "输入格式为搜索提示词，例如：'深圳湾公园露营'、'松山湖露营地'等。"
        "返回图片的URL链接。"
    )

    def _run(self, query: str) -> str:
        try:
            # 处理输入格式
            if isinstance(query, str):
                # 如果输入是JSON字符串，尝试解析
                if query.startswith('{'):
                    try:
                        query_data = json.loads(query)
                        query = query_data.get('query', '')
                    except json.JSONDecodeError:
                        pass
                
                # 处理Unicode转义序列
                query = query.encode().decode('unicode_escape')
            
            # 从环境变量获取SerperDev API密钥
            serper_api_key = os.getenv('SERPER_API_KEY')
            if not serper_api_key:
                return "错误：未找到SerperDev API密钥，请检查.env文件中的SERPER_API_KEY配置"
            
            # 构建API请求
            url = "https://google.serper.dev/images"
            headers = {
                'X-API-KEY': serper_api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                'q': query,
                'num': 5  # 返回5张图片
            }
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if 'images' in data:
                image_urls = [img['imageUrl'] for img in data['images']]
                return "\n".join(image_urls)
            else:
                return f"无法获取图片，API返回：{data}"
                
        except Exception as e:
            return f"获取图片失败: {str(e)}"