import gradio as gr
import pickle
import os
import subprocess

subprocess.Popen(
    ["python", "backend.py"]
)

default_params = "-R 100 --no-playlist --retry-sleep fragment:exp=1:10"
def add_queue(url, params):
    cmd = ["yt-dlp", url] + params.split(" ")
    if not os.path.exists("queue.pkl"):
        with open("queue.pkl","wb") as f:
            pickle.dump([], f)
    with open("queue.pkl","rb") as f:
        queue = pickle.load(f)
    queue.append(cmd)
    with open("queue.pkl","wb") as f:
        pickle.dump(queue,f)
    return "Started: " + url

def clear():
    os.remove("queue.pkl")
    return "Cleared"

# Build gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Video downloader based on yt-dlp")

    url = gr.Textbox(label="URL")
    params = gr.Textbox(label="Parameters", value=default_params)
    status = gr.Textbox(label="status")
    download_button = gr.Button("Download")
    clear_button = gr.Button("Clear")
    download_button.click(fn=add_queue, inputs=[url, params],outputs=status)
    clear_button.click(fn=clear, outputs=[status])

    
demo.launch()