import json
import os
import random
from dotenv import load_dotenv
import httpx
from crewai_tools import MCPServerAdapter
from crewai.agents.agent_builder.base_agent import BaseTool
from typing import List, Dict, Any

import requests
 
# MCP 配置文件
config: Dict[str, Dict[str, Any]] = {
    "amap-maps": {
        "url": "https://mcp.amap.com/sse?key=702737fc38cd2727a2893002c58c4e29",  # SSE 服务器地址
        "headers": {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

    }
}
 
def get_mcp_gaode_see_tools() -> List[BaseTool]:
    """
    根据配置加载所有 MCP 工具并转换为 CrewAI 兼容的 BaseTool
    :return: list[BaseTool]
    """

        # 创建MCPServerAdapter对象
    adapter = MCPServerAdapter({"url": "https://mcp.amap.com/sse?key=702737fc38cd2727a2893002c58c4e29"})
    # 将adapter中的tools添加到tools列表中
    tools = adapter.tools
    
    return tools

load_dotenv("/home/gpu/work/my_first_crewai/.env")

key = os.getenv("AMAP_KEY")

# 获取经纬度
def get_jw(address):
    response = requests.get(f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={key}')
    response = json.loads(response.text)
    return response['geocodes'][0]['location']


def get_keyword_search(keyword,location,type,radius=40000):
    #response = requests.get(f"https://restapi.amap.com/v3/place/around?key={key}&location={location}&keywords={keyword}&radius={radius}&types=110000")
    
    response = requests.get(f"https://restapi.amap.com/v5/place/around?key={key}&location={location}&keywords={keyword}&radius={radius}&types={type}&show_fields=photos&page_size=60")


    response = json.loads(response.text)
    response = get_summary_search(response)
    return response

def get_summary_search(response):
    summary_list = []
    random.shuffle(response['pois'])
    spot_list = response['pois'][:5]
    for one in spot_list:
        summary = {}
        summary['景点名称']=one['name']
        summary['图片网址'] = []
        if one.get('photos',[]) != []:
            for one_pic in  one["photos"]:
                summary['图片网址'].append(one_pic["url"])
        summary_list.append(summary)
    return summary_list




if __name__ == "__main__":
    location = get_jw("东莞松山湖")
    get_keyword_search(keyword='美食',location=location,type='050000')
    get_keyword_search("露营",location,radius=50000,type='110000')
    get_jw("东莞")
    tools = get_mcp_gaode_see_tools()
    
    for tool in tools:
        print(tool)
