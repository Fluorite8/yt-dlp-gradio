import os
import subprocess
import gradio as gr
from filelock import FileLock
import json
from functools import partial
from utils import gen_job_info, job_tag, MAX_JOBS, CONFIG_FILE, JOB_LIST_FILE, DFAULT_CONFIG, FILE_LOCK, MAX_WORKERS


# Create the config and job list if it doesn't exist
with FileLock(FILE_LOCK, timeout=5):
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DFAULT_CONFIG, f)
    if not os.path.exists(JOB_LIST_FILE):
        with open(JOB_LIST_FILE, "w") as f:
            json.dump([], f)

# Create tmp dir if it doesn't exist
if not os.path.exists("tmp"):
    os.mkdir("tmp")

# Job status: pending, running, paused, finished, error
# On startup, all running jobs are reset to pending, since no worker is running at this moment.
with FileLock(FILE_LOCK, timeout=5):
    with open(JOB_LIST_FILE, "r") as f:
        job_list = json.load(f)
    # reset all running jobs to pending
    for job in job_list:
        if job["status"] == "running":
            job["status"] = "pending"
            job["worker"] = None
            job["progress"] = ""

    with open(JOB_LIST_FILE, "w") as f:
        json.dump(job_list, f)
    
# Open MAX_WORKERS worker process with the same python interpreter
# wrokers are assigned with --worker_id
for i in range(MAX_WORKERS):
    subprocess.Popen(["python", "worker.py", "--worker_id", str(i)])

def add_job(url, params):
    with FileLock(FILE_LOCK, timeout=5):
        with open(JOB_LIST_FILE, "r") as f:
            job_list = json.load(f)
        # Check capacity
        if len(job_list) >= MAX_JOBS:
            return "[ERROR] Job list is full, please remove some jobs before adding new ones."
        # Check duplication job_tag (generates a unique tag with url and params)
        if job_tag(url, params) in [job_tag(job["url"], job["params"]) for job in job_list]:
            return "[ERROR] Job already exists, please change the url or params."

        # Add job
        job_list.append({
            "url": url, 
            "params": params,
            "status": "pending",
            "progress": "",
            "worker": None
        })
        with open(JOB_LIST_FILE, "w") as f:
            json.dump(job_list, f)
    return f"[OK] Job added successfully, url = {url}"

def job_list_update():
    # Load job list
    with FileLock(FILE_LOCK, timeout=5):
        with open(JOB_LIST_FILE, "r") as f:
            job_list = json.load(f)
    num_job = len(job_list)

    # Assign gradio components
    txt = [None] * MAX_JOBS
    btn_pause = [None] * MAX_JOBS
    btn_remove = [None] * MAX_JOBS
    btn_resume = [None] * MAX_JOBS
    spl_line = [None] * MAX_JOBS
    for j in range(MAX_JOBS):
        if j < num_job:
            txt[j] = gr.Markdown(gen_job_info(job_list[j]),label=f"Job {j+1}", visible=True)
            btn_pause[j] = gr.Button(f"Pause Job {j+1}", visible= True)
            btn_remove[j] = gr.Button(f"Remove Job {j+1}", visible=True)
            btn_resume[j] = gr.Button(f"Resume Job {j+1}", visible=True)
            spl_line[j] = gr.Markdown("---", visible=True)
        else:
            txt[j] = gr.Markdown(visible=False)
            btn_pause[j] = gr.Button(f"Pause Job {j+1}", visible= False)
            btn_remove[j] = gr.Button(f"Remove Job {j+1}", visible=False)
            btn_resume[j] = gr.Button(f"Resume Job {j+1}", visible=False)
            spl_line[j] = gr.Markdown("---", visible=False)

    return txt+btn_pause+btn_remove+btn_resume+spl_line

def get_settings():
    # Read default params from config
    with FileLock(FILE_LOCK, timeout=5):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    return config

def update_settings_fn(n_worker, default_param):
    # Update config
    with FileLock(FILE_LOCK, timeout=5):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        config["threads"] = n_worker
        config["params"] = default_param
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    return "Done."

def pause_job(id):
    # Pause a job
    with FileLock(FILE_LOCK, timeout=5):
        with open(JOB_LIST_FILE, "r") as f:
            job_list = json.load(f)
        if job_list[id]["status"] == "running" or job_list[id]["status"] == "pending":
            job_list[id]["status"] = "paused"
        with open(JOB_LIST_FILE, "w") as f:
            json.dump(job_list, f)
    return job_list_update()

def resume_job(id):
    # Resume a job
    with FileLock(FILE_LOCK, timeout=5):
        with open(JOB_LIST_FILE, "r") as f:
            job_list = json.load(f)
        if job_list[id]["status"] == "paused":
            job_list[id]["status"] = "pending"
        with open(JOB_LIST_FILE, "w") as f:
            json.dump(job_list, f)
    return job_list_update()

def remove_job(id):
    # Remove a job 
    with FileLock(FILE_LOCK, timeout=5):
        with open(JOB_LIST_FILE, "r") as f:
            job_list = json.load(f)
        job_list.pop(id)
        with open(JOB_LIST_FILE, "w") as f:
            json.dump(job_list, f)
    return job_list_update()


with gr.Blocks() as demo:
    
    txt = [None] * MAX_JOBS
    btn_pause = [None] * MAX_JOBS
    btn_remove = [None] * MAX_JOBS
    btn_resume = [None] * MAX_JOBS
    spl_line = [None] * MAX_JOBS

    with gr.Tab("Download") as tab_dl:
        url = gr.Textbox(label="URL")
        params = gr.Textbox(label="Params", lines=5, value=get_settings()["params"], interactive=True)
        btn_down = gr.Button("Download")
        result = gr.Textbox(label="Result")

        btn_down.click(fn=add_job, inputs=[url, params], outputs=result)
        

    with gr.Tab("Job List") as tab_jl:
        for i in range(MAX_JOBS):
            with gr.Row():
                txt[i] = gr.Markdown("Textbox", label="Job", visible=False)
            with gr.Row():
                with gr.Column():
                    btn_pause[i] = gr.Button(f"Pause Job", visible= False)
                with gr.Column():
                    btn_resume[i] = gr.Button(f"Resume Job", visible=False)
                with gr.Column():
                    btn_remove[i] = gr.Button(f"Remove Job", visible=False)
            with gr.Row():
                spl_line[i] = gr.Markdown("---", visible=False)
        for i in range(MAX_JOBS):
            btn_pause[i].click(fn=partial(pause_job,i), inputs=None,
                outputs=txt+btn_pause+btn_remove+btn_resume+spl_line
            )
            btn_remove[i].click(fn=partial(remove_job,i), inputs=None,
                outputs=txt+btn_pause+btn_remove+btn_resume+spl_line
            )
            btn_resume[i].click(fn=partial(resume_job,i), inputs=None,
                outputs=txt+btn_pause+btn_remove+btn_resume+spl_line  
            )

    
    with gr.Tab("Settings") as tab_set:
        threads = gr.Slider(1, MAX_WORKERS, step=1, label="Threads", interactive=True)
        default_param = gr.Textbox(label="Default Params", lines=5)
        result = gr.Textbox(label="Result")
        update_settings = gr.Button("Update Settings")


        update_settings.click(
            fn = update_settings_fn,
            inputs=[threads, default_param],
            outputs=result
        )

    tab_jl.select(
        fn = job_list_update,
        inputs = None,
        outputs = txt+btn_pause+btn_remove+btn_resume+spl_line,
    )
    
    tab_dl.select(
        fn = lambda: get_settings()["params"],
        inputs = None,
        outputs = params
    )

    tab_set.select(
        fn=lambda: [get_settings()["params"], get_settings()["threads"]],
        inputs=None,
        outputs=[default_param, threads]
    )

demo.launch()