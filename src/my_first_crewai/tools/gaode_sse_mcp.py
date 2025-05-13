import os
import httpx
from crewai_tools import MCPServerAdapter
from crewai.agents.agent_builder.base_agent import BaseTool
from typing import List, Dict, Any
 
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

if __name__ == "__main__":
    tools = get_mcp_gaode_see_tools()
    for tool in tools:
        print(tool)
