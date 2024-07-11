import time
import subprocess
import os
import json
from filelock import FileLock
import argparse

from utils import gen_job_info, job_tag, MAX_JOBS, CONFIG_FILE, JOB_LIST_FILE, DFAULT_CONFIG, FILE_LOCK, MAX_WORKERS

# Get my worker id from argparse, raise error if id is not in range
parser = argparse.ArgumentParser()
parser.add_argument('--worker_id', type=int, required=True)
args = parser.parse_args()

if args.worker_id < 0 or args.worker_id >= MAX_WORKERS:
    raise ValueError(f'Invalid worker id: {args.worker_id}')


# Each job and each worker works as a finite state machine:
# Job status can be: pending, running, paused, finished, error
# Worker status can be: inactive, idle, running(binding to job), finished, error

# The behavior of the worker machine is as follows:
# Worker with id greater than config["threads"] will be inactive
# Worker in idle will try to bind to a job with status pending, if no job is available, worker will sleep for a while and try again
# If the job which a running worker is binding to is paused or directly removed, the worker will drop the job and return to idle status
# When running worker comes to finished or error, the worker will set the job status to finished or error and return to idle status

my_status = "idle"
my_proc = None


def start_job(job):
    global my_proc
    global my_status
    # Start downloading the job
    tag = job_tag(job["url"], job["params"])
    print(f"Worker {args.worker_id} is starting job {tag}")
    sh_cmd = f"yt-dlp {job['url']} {job['params']} -o tmp/{tag}.mp4 > tmp/{tag}.log 2>&1"
    print(sh_cmd)
    my_proc = subprocess.Popen(sh_cmd, shell=True)
    # Set my status to running
    my_status = "running"

def drop_job(job):
    global my_proc
    global my_status
    # Kill the job process
    print(f"Worker {args.worker_id} is dropping job {job_tag(job['url'], job['params'])}")
    my_proc.kill()
    my_proc = None
    # Set my status to idle
    my_status = "idle"

def check_success(job):
    tag = job_tag(job["url"], job["params"])
    return os.path.exists(f"tmp/{tag}.mp4")

while True:
    time.sleep(10)
    # Check if I'm an inactive worker
    with FileLock(FILE_LOCK, timeout=5):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    if args.worker_id >= config["threads"]:
        # I'm a inactive worker, sleep for a while and try again
        # print(f"Worker {args.worker_id} is inactive")
        continue
    
    # Check if I'm an idle worker
    if my_status == "idle":
        # print(f"Worker {args.worker_id} is in idle")
        # Try to bind to a job with status pending
        with FileLock(FILE_LOCK, timeout=5):
            with open(JOB_LIST_FILE, 'r') as f:
                job_list = json.load(f)
            for job_id in range(len(job_list)):
                if job_list[job_id]["status"] == "pending":
                    # Bind to the job
                    job_list[job_id]["status"] = "running"
                    job_list[job_id]["worker"] = args.worker_id
                    # Start job
                    start_job(job_list[job_id])
                    break
            with open(JOB_LIST_FILE, 'w') as f:
                json.dump(job_list, f)
    
    # Check if I'm a running worker
    if my_status == "running":
        # print(f"Worker {args.worker_id} is running")
        # Check if my job is paused or removed
        with FileLock(FILE_LOCK, timeout=5):
            with open(JOB_LIST_FILE, 'r') as f:
                job_list = json.load(f)
            # find my job_id
            job_id = -1
            for idx in range(len(job_list)):
                if job_list[idx]["worker"] == args.worker_id:
                    job_id = idx

            if job_id == -1:
                # The job which I'm binding to is removed, return to idle status
                my_status = "idle"

            elif job_list[job_id]["status"] == "paused":
                # Drop the job
                drop_job(job_list[job_id])
                # Set worker to None
                job_list[job_id]["worker"] = None

            elif job_list[job_id]["status"] == "running":
                # if my_proc exited, check if the job is successful
                if my_proc.poll() is not None:
                    # Check if the job is successful
                    if check_success(job_list[job_id]):
                        # Set the job status to success
                        job_list[job_id]["status"] = "finished"
                    else:
                        # Set the job status to failed
                        job_list[job_id]["status"] = "error"
                    job_list[job_id]["worker"] = None
                    # Set the worker status to idle
                    my_status = "idle"  

            with open(JOB_LIST_FILE, 'w') as f:
                json.dump(job_list, f)