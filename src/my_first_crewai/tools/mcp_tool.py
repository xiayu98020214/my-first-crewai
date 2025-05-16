import json
import os
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from mcp import StdioServerParameters
from crewai.agents.agent_builder.base_agent import BaseTool
from typing import List, Dict, Any

import requests
from my_first_crewai.const import ENV_FILE

load_dotenv(ENV_FILE)
key = os.getenv("AMAP_KEY")

# MCP 配置文件
config: Dict[str, Dict[str, Any]] = {
    "amap-maps": {
      "command": "npx",
      "args": ["-y", "@amap/amap-maps-mcp-server"],
      "env": {
        "AMAP_MAPS_API_KEY": key,
        "AMAP_API_KEY": key
      }
    }
}

def get_mcp_gaode_tools() -> List[BaseTool]:
        """
        根据配置加载所有 MCP 工具并转换为 CrewAI 兼容的 BaseTool
        :return: list[BaseTool]
        """
        tools:List[BaseTool] = []
        for server_config in config.items():
            # 从server_config中获取command、args、env参数，并创建StdioServerParameters对象
            server_params = StdioServerParameters(
                command=server_config[1]["command"],
                args=server_config[1].get("args", []),
                env=server_config[1].get("env", {})
            )
            # 创建MCPServerAdapter对象
            adapter = MCPServerAdapter(server_params)
            # 将adapter中的tools添加到tools列表中
            tools.extend(adapter.tools)
        
        #驾车
        # result_tools = []
        # for tool in tools:
        #     if tool.name == 'maps_regeocode':
        #         result_tools.append(tool)

        #     if tool.name == 'maps_geo':
        #          result_tools.append(tool)

        #     if tool.name == "maps_direction_driving":
        #         result_tools.append(tool)
        return tools

all_gaode_tools = get_mcp_gaode_tools()

def get_maps_geo_func():
    for tool in all_gaode_tools:
      if tool.name == "maps_geo":
          return tool
           #result = tool.run({"city":"东莞"})
          
#gaode_maps_geo_tool = get_maps_geo_func()


def get_maps_around_search_func():
    for tool in all_gaode_tools:
      if tool.name == "maps_around_search":
          return tool

#gaode_maps_around_search_tool = get_maps_around_search_func()





if __name__ == "__main__":
    # tools = get_mcp_gaode_tools()
    # for tool in tools:
    #   if tool.name == "maps_geo":
    #        result = tool.run({"city":"东莞"})
    #        print(result)
        
    # result = gaode_maps_geo_tool.run({"city":"东莞"})   
    # print(gaode_maps_around_search_tool.description)
    # print(gaode_maps_around_search_tool.args_schema)
   # result2 = gaode_maps_around_search_tool.run({"keywords": "餐厅", "location": "113.889699,22.934925","radius": "1000"})
#     result2 = gaode_maps_around_search_tool.run({
#   "keywords": "健身房",
#   "location": "116.4738,39.9088",  
#   "radius": "1000"
# })

    # print(result2)


  pass
