#!/usr/bin/env python
import json
import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from my_first_crewai.tools.gaode_sse_mcp import get_jw, get_keyword_search
from my_first_crewai.tools.markdown_pdf import markdown_to_pdf
from my_first_crewai.tools.travel_tools import IPLocationTool, WeatherTool
from pydantic import BaseModel, Field
from crewai import LLM
from crewai.flow.flow import Flow, listen, start
from openai import OpenAI
# Define our models for structured data
load_dotenv("/home/gpu/work/my_first_crewai/.env")
key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    api_key=key,
    base_url="https://api.deepseek.com",
)

llm = LLM(
    model="deepseek/deepseek-chat",
    stream=True,
    temperature=0.9,
    #api_base="https://api.deepseek.com"    
)





# Define our flow state
class GuideOutline(BaseModel):
    source: str = Field(default="",description="出发地")
    source_ll: str = Field(default="",description="出发地经纬度")
    destination: str = Field(default="",description="目的地")
    destination_ll: str = Field(default="",description="目的地经纬度")
    start_date: str = Field(default="",description="出发日期")
    during: str = Field(default="",description="天数")
    camp_out: str = Field(default="",description="露营地")
    food: str = Field(default="",description="美食")
    weather: str = Field(default="",description="天气")

class GuideCreatorState(BaseModel):
    input_text: str = Field(default="", description="用户输入")
    guide_outline: GuideOutline = Field(default=GuideOutline(), description="游记大纲")
    result: str  = Field(default="", description="输出md文档")


start_time = 0
class GuideCreatorFlow(Flow[GuideCreatorState]):
    """Flow for creating a comprehensive guide on any topic"""

    @start()
    def get_user_input(self):
       

        return self.state

    @listen(get_user_input)
    def create_guide_outline(self, state):
        """Create a structured outline for the guide using a direct LLM call"""
        print("Creating guide outline...")

        global start_time

        start_time = time.time()
        # Create the messages for the outline
        messages = [
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": f"""
             用户输入：{state.input_text}
             请根据用户输入，提取一下信息。如果没有提取到，用未提及代替。输出用json格式。
             1. 出发地
             2. 目的地
             3. 出发日期
             4. 行程天数
             5. 用户的兴趣爱好

            举例：
            用户输入："2025.5.14出发，我31岁有两个孩子，从深圳到东莞松山湖，自驾游2天"
            JSON输出格式：
             {{
                "source": "深圳",
                "destination": "东莞松山湖",
                "start_date": "2025.5.14",
                "during": "2",
                "interest": "历史"
             }}
            """}

        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
            response_format={
                    'type': 'json_object'
            }
        )

        # Parse the JSON response
        outline_dict = json.loads(response.choices[0].message.content)  

        if outline_dict['source'] == '未提及':
            outline_dict['source'] = "东莞松山湖"
        outline_dict['source_ll'] = get_jw(outline_dict['source'])
        if outline_dict['destination'] == '未提及':
            outline_dict['destination'] = "东莞松山湖"
        outline_dict['destination_ll'] = get_jw(outline_dict['destination'])
        
        outline_dict['camp_out'] = str(get_keyword_search(keyword='露营',location=outline_dict['destination_ll'],type='110000'))
        outline_dict['food'] =  str(get_keyword_search(keyword='美食',location=outline_dict['destination_ll'],type='050000'))
        self.state.guide_outline = GuideOutline(**outline_dict)
   #     outline_dict['weather'] = WeatherTool()._run(outline_dict['source'])
        print(f"work flow during_time:", time.time()-start_time)
        print("camp_out:", outline_dict['camp_out'])
        print("food:", outline_dict['food'])
        return self.state.guide_outline

    @listen(create_guide_outline)
    def write_and_compile_guide(self, outline):
        # Create the messages for the outline
        messages = [
            {"role": "system", "content": "你是一名活动规划师，研究并找到目的地有趣的活动，包括适合旅行者兴趣和年龄组的活动和事件。"},
            {"role": "user", "content": f"""
重点关注适合露营者兴趣和年龄组以及同行人员的活动和事件。
用户输入{self.state.input_text}：
- 出发地：{outline.source}
- 目的地：{outline.destination}
- 旅行时长：{outline.during}
- 出发时间：{outline.start_date}
- 景点：{outline.camp_out}
- 美食：{outline.food}

重点关注适合露营者兴趣和年龄组以及同行人员的活动和事件。
输出：
    每天推荐的活动和事件列表。    
    每个条目应包括活动名称、位置、图片、简短描述，以及为什么适合该旅行者。    
    所有内容必须使用简体中文输出。


注意：输出以markdown形式输出。
        """}

        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            

        )
        result = response.choices[0].message.content


        print(f"all time during_time:", time.time()-start_time)
        

        url = get_amap_url(self.state)
        content = f"[高德导航]({url})"
        result = result + "\n" + content
        result = result.replace("```markdown", "").replace("```", "")
        file_path2 = r"/home/gpu/work/my_first_crewai/output/report.txt"  # 替换为实际的文件路径      

        
        with open(file_path2, 'w', encoding='utf-8') as file:
            file.write(result)     
        #markdown_to_pdf(result, file_path)

        self.state.result = result
        return result

def kickoff():
    """Run the guide creator flow"""
    ask = "2025.5.14出发，我31岁有两个孩子，到东莞松山湖，自驾游2天"
    result = GuideCreatorFlow().kickoff(inputs={"input_text": ask})
    print("result1111111111:",result)


def plot():
    """Generate a visualization of the flow"""
    flow = GuideCreatorFlow()
    flow.plot("guide_creator_flow")
    print("Flow visualization saved to guide_creator_flow.html")

def get_amap_url(state):
    source = state.guide_outline.source_ll
    destination = state.guide_outline.destination_ll
    print("source:",source)
    print("destination",destination)
    url = f"https://uri.amap.com/navigation?from={source}&to={destination}&mode=car"
    return url



def summary_result(content):
    messages = [
            {"role": "system", "content": "你是一名语言老师，擅长总结和归纳。"},
            {"role": "user", "content": f"""                
            请根据下边的内容，提炼总结核心的信息，不要包括图片和位置信息。

            输入：{content}

            结果：
            """}

        ]
    
    response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,

        )
    return response.choices[0].message.content



if __name__ == "__main__":
    with open(r"/home/gpu/work/my_first_crewai/output/report.txt", "r", encoding="utf-8") as file:
        content = file.read()
    summary = summary_result(content)
    print("summary:",summary)
    
    #kickoff()