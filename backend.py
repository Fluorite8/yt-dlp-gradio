import time
import subprocess
import os
import pickle

def backend():
    while True:
        time.sleep(10)
        print("Running")
        if os.path.exists("queue.pkl"):
            with open("queue.pkl","rb") as f:
                queue = pickle.load(f)
            for cmd in queue:
                subprocess.run(cmd)

backend()