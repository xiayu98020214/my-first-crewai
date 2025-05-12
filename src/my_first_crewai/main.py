#!/usr/bin/env python
import sys
import warnings
import gradio as gr
import threading
import queue
import time

from datetime import datetime

from my_first_crewai.crew import MyFirstCrewai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# 假设任务名
TASK_NAMES = ["任务1", "任务2", "任务3"]

def run():
    """
    Run the crew.
    """
    inputs = {
        'origin': '深圳',
        'destination': '东莞, 松山湖',
        'age': 31,
        'hotel_location': '松山湖',
        'flight_information': '自驾',
        'trip_duration': '2天'
    }
    
    try:
        crew = MyFirstCrewai().crew()
        crew.task_callback = task_callback
        MyFirstCrewai().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        MyFirstCrewai().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MyFirstCrewai().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        MyFirstCrewai().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


task_names_no = 0
def run_crew_stream(origin, destination, age, hotel_location, flight_information, trip_duration):
    q = queue.Queue()
    history = {name: "" for name in TASK_NAMES}

    def task_callback(output):
        global task_names_no
        msg = f"Task: {output.description}\nOutput: {output.raw}\n"
        q.put((TASK_NAMES[task_names_no], msg))
        task_names_no += 1

    def crew_thread():
        crew = MyFirstCrewai().crew()
        crew.task_callback = task_callback
        crew.kickoff(inputs={
            'origin': origin,
            'destination': destination,
            'age': age,
            'hotel_location': hotel_location,
            'flight_information': flight_information,
            'trip_duration': trip_duration
        })
        q.put((None, None))  # 结束信号

    threading.Thread(target=crew_thread, daemon=True).start()

    while True:
        task_name, item = q.get()
        if task_name is None:
            break
        if task_name in history:
            history[task_name] += item + "\n"
        yield [history[name] for name in TASK_NAMES]
        time.sleep(0.1)

with gr.Blocks() as demo:
    gr.Markdown("# CrewAI 多任务流式演示")
    with gr.Row():
        origin = gr.Textbox(label="Origin", value="深圳")
        destination = gr.Textbox(label="Destination", value="东莞, 松山湖")
        age = gr.Number(label="Age", value=31)
        hotel_location = gr.Textbox(label="Hotel Location", value="松山湖")
        flight_information = gr.Textbox(label="Flight Information", value="自驾")
        trip_duration = gr.Textbox(label="Trip Duration", value="2天")
    with gr.Row():
        task_outputs = [gr.Textbox(label=name, lines=10) for name in TASK_NAMES]

    btn = gr.Button("开始任务")
    btn.click(
        run_crew_stream,
        inputs=[origin, destination, age, hotel_location, flight_information, trip_duration],
        outputs=task_outputs,
        api_name="run_crew_stream"
    )

if __name__ == "__main__":
    demo.launch()