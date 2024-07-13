import hashlib
import os

MAX_JOBS = 15
MAX_WORKERS = 5
CONFIG_FILE = "config.json"
JOB_LIST_FILE = "job_list.json"
FILE_LOCK = "file.lock"
DFAULT_CONFIG = {
    "threads": 3,
    "params": "-R 100 --no-playlist --retry-sleep linear=1:10:2 --abort-on-unavailable-fragments",
    "output_dir": os.path.join(os.getcwd(), "YtDownloads/")
}

USER_CACHE = os.path.join(os.environ['HOME'], ".cache/")
if not os.path.exists(USER_CACHE):
    os.mkdir(USER_CACHE)

CACHE_DIR = os.path.join(USER_CACHE, "yt-dlp-gradio/")
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

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
        with open(os.path.join(CACHE_DIR, f"{tag}.log"), "r") as f:
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