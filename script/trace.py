import json
import subprocess
import os
from utils import GitFileRetriever,cleanup_directory,diff_format,create_github_issue
import datetime
token = os.environ.get('GITHUB_TOKEN')
repo_id = os.environ.get('REPO_NAME')
assert token,"plese add auth token trace_token in the secrte"
assert os.path.exists("trace_record.json"),"Not found trace_record.json.please edit init_file.txt and init_trace."
trace_data=json.load(open('trace_record.json','r',encoding='utf-8'))
repo_url=trace_data['repo_url']

#clone repo
try:
    subprocess.run(['git', 'clone', repo_url], check=True)
except subprocess.CalledProcessError:
    raise "Git clone failed please check the repo url and try again"

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

cleanup_directory(flod_name)

if len(diff_result)>0:
    issue_title=f"diff[{trace_data['datetime'][-2]}-{trace_data['datetime'][-1]}]"
    issue_body=diff_format(diff_result)
    create_github_issue(repo_id,issue_title,issue_body,token)
else:
    print(f"No diff between {trace_data['datetime'][-2]} and {trace_data['datetime'][-1]}")

trace_data['datetime'].append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
json.dump(trace_data,open('trace_record.json','w',encoding='utf-8'),indent=4)