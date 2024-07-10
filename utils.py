import hashlib

MAX_JOBS = 15
MAX_WORKERS = 5
CONFIG_FILE = "config.json"
JOB_LIST_FILE = "job_list.json"
FILE_LOCK = "file.lock"
DFAULT_CONFIG = {
    "threads": 3,
    "params": "-R 100"
}

def job_tag(url:str, params:str):
    # Generate a unique tag for a job based on its URL and parameters
    # tag is equal to first 6 characters of the md5 hash of the URL and parameters
    tag = hashlib.md5((url + params).encode()).hexdigest()[:6]
    return tag

def trim_string(s, max_length=30):
    if len(s) <= max_length:
        return s
    else:
        half_max = max_length // 2
        return s[:half_max - 3] + " ... " + s[-(max_length - half_max + 3):]

def gen_job_info(job):
    tag = job_tag(job["url"], job["params"])
    # Try to read last 3 lines of tmp/{tag}.log
    try:
        with open(f"tmp/{tag}.log", "r") as f:
            progress = f.readlines()[-3:]
    except:
        progress = ["No progress log found"]
    # Concatenate progress lines into a string
    progress = "".join(progress)

    job_info = \
f"""### Job {tag}
| status | {job["status"]} |
| --- | --- |
| worker | {job["worker"]} |
| URL | {trim_string(job["url"])} |

progress: 
```
{progress}
```
"""
    return job_info