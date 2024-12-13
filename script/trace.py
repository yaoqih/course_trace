import json
import subprocess
import os
from utils import GitFileRetriever
import datetime

trace_data=json.load(open('trace_record.json','r',encoding='utf-8'))
repo_url=trace_data['repo_url']

#clone repo
# try:
#     subprocess.run(['git', 'clone', repo_url], check=True)
# except subprocess.CalledProcessError:
#     raise "Git clone failed please check the repo url and try again"

flod_name=repo_url.split('/')[-1]
if not os.path.exists(flod_name):
    raise f"Could not find the flod {flod_name} after git clone"

retriever = GitFileRetriever(flod_name)

diff_result={}
for file in trace_data['trace_record']:
    diff=retriever.get_file_diff(file,trace_data['trace_record'][file]['commit_ids'][-1])
    if diff:
        diff_result[file]=diff
    trace_data['trace_record'][file]['commit_ids'].append(retriever.largest_commit)
trace_data['datetime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
json.dump(trace_data,open('trace_record.json','w',encoding='utf-8'),indent=4)
