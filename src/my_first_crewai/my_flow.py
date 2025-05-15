#!/usr/bin/env python
import json
import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from my_first_crewai.crew import MyFirstCrewai
from my_first_crewai.tools.gaode_sse_mcp import get_jw, get_keyword_search
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
    # weather: str = Field(default="",description="天气")

class GuideCreatorState(BaseModel):
    input_text: str = Field(default="", description="用户输入")
    guide_outline: GuideOutline = Field(default=GuideOutline(), description="游记大纲")



class GuideCreatorFlow(Flow[GuideCreatorState]):
    """Flow for creating a comprehensive guide on any topic"""

    @start()
    def get_user_input(self):
       

        return self.state

    @listen(get_user_input)
    def create_guide_outline(self, state):
        """Create a structured outline for the guide using a direct LLM call"""
        print("Creating guide outline...")



        start_time = time.time()
        # Create the messages for the outline
        messages = [
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": f"""
             用户输入：{state.input_text}
             请根据用户输入，提取一下信息。输出用json格式。
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
        outline_dict['source_ll'] = get_jw(outline_dict['source'])
        outline_dict['destination_ll'] = get_jw(outline_dict['destination'])
        outline_dict['camp_out'] = str(get_keyword_search(keyword='露营',location=outline_dict['destination_ll'],type='110000'))
        outline_dict['food'] =  str(get_keyword_search(keyword='美食',location=outline_dict['destination_ll'],type='050000'))
        self.state.guide_outline = GuideOutline(**outline_dict)
        print(f"work flow during_time:", time.time()-start_time)
        return self.state.guide_outline

    @listen(create_guide_outline)
    def write_and_compile_guide(self, outline):
        start_time = time.time()

        result = MyFirstCrewai().crew().kickoff(inputs={
            "input_text": self.state.input_text,
            "source": outline.source,
            "destination": outline.destination,
            "destination_ll": outline.destination_ll,
            "start_date": outline.start_date,            
            "during": outline.during,
            "camp_out":outline.camp_out,
            "food": outline.food
        })
        print(f"crew during_time:", time.time()-start_time)

        return result

def kickoff():
    """Run the guide creator flow"""
    ask = "2025.5.14出发，我31岁有两个孩子，从深圳到东莞松山湖，自驾游2天"
    result = GuideCreatorFlow().kickoff(inputs={"input_text": ask})
    print("result1111111111:",result)


def plot():
    """Generate a visualization of the flow"""
    flow = GuideCreatorFlow()
    flow.plot("guide_creator_flow")
    print("Flow visualization saved to guide_creator_flow.html")

if __name__ == "__main__":
    kickoff()