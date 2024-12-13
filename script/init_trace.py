import shutil
import os
import json
import traceback
from utils import filter_ignored_files,GitFileRetriever,cleanup_directory
import subprocess
import datetime

#init variables
init_file_name='init_file.txt'
trace_record_file_name='trace_record.json'
trace_record={}
trace_record_temp={}
line_count=1

assert os.path.exists(init_file_name),f"Not fond {init_file_name}.txt! Program don't know what repo to trace"

#parse init file
with open(init_file_name) as f:
    repo_url=f.readline().strip()
    for line in f.readlines():
        line_count+=1
        if line.strip():
            if line.count(":")==0:
                trace_record_temp[line.strip()]={'commit_id':'','line_number':line_count}
            elif line.count(":")==1:
                trace_record_temp[line.split(':')[0]]={'commit_id':line.split(':')[1],'line_number':line_count}
            else:
                raise f"Parse file {init_file_name} in line {line_count}, please check the the number of :"
#clone repo
try:
    subprocess.run(['git', 'clone', repo_url], check=True)
except subprocess.CalledProcessError:
    raise "Git clone failed please check the repo url and try again"
flod_name=repo_url.split('/')[-1]
if not os.path.exists(flod_name):
    raise f"Could not find the flod {flod_name} after git clone"

#check the rules 
for file_rule in trace_record_temp.keys():
    matching_files=filter_ignored_files(flod_name,[file_rule])
    if len(matching_files)==0:
        print(f"Warning! Could not find the any file by using rules {file_rule} line {trace_record_temp[file_rule]['line_number']} in the repo {flod_name}")
    elif len(matching_files)>1:
        print(f"Fond {len(matching_files)} file by using rules {file_rule} line {trace_record_temp[file_rule]['line_number']} in the repo {flod_name}")
    # trace_record.update({file:trace_record_temp[file_rule]['commit_id'] for file in matching_files})
    trace_record_temp[file_rule]['files']=matching_files

#commit check
retriever = GitFileRetriever(flod_name)
for file_rule in trace_record_temp.keys():
    for file in trace_record_temp[file_rule]['files']:
        try:
            commit_id=trace_record_temp[file_rule]['commit_id']
            if commit_id =='':
                commit_id=retriever.repo.head.commit.hexsha
                trace_record[file]={'commit_ids':[commit_id]}
            else:
                content = retriever.get_file_content(file, commit_id)
                trace_record[file]={'commit_ids':[commit_id]}
        except Exception as e:
            print(f"Error! Get file content failed {file} in commit {commit_id} with error {str(e)}, Please check the rules {file_rule} in line {trace_record_temp[file_rule]['line_number']}")
            traceback.print_exc()
            continue

#save and clean up
retriever.close()
json.dump({"trace_record":trace_record,"repo_url":repo_url,'datetime':[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]},open(trace_record_file_name,'w',encoding='utf-8'),indent=4)
cleanup_directory(flod_name)