import os
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from crewai.agents.agent_builder.base_agent import BaseTool
from typing import List, Dict, Any
 
# MCP 配置文件
config: Dict[str, Dict[str, Any]] = {
    "amap-maps": {
      "command": "npx",
      "args": ["-y", "@amap/amap-maps-mcp-server"],
      "env": {
        "AMAP_MAPS_API_KEY": "702737fc38cd2727a2893002c58c4e29",
        "AMAP_API_KEY": "702737fc38cd2727a2893002c58c4e29"
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

if __name__ == "__main__":
    tools = get_mcp_gaode_tools()
    print(tools)