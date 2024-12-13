import json
import subprocess
import os
trace_data=json.load(open('trace_record.json',encoding='utf-8'),'r')
repo_url=trace_data['repo_url']

#clone repo
try:
    subprocess.run(['git', 'clone', repo_url], check=True)
except subprocess.CalledProcessError:
    raise "Git clone failed please check the repo url and try again"
flod_name=repo_url.split('/')[-1]
if not os.path.exists(flod_name):
    raise f"Could not find the flod {flod_name} after git clone"


