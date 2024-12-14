import os
import pathspec
import git
from pathlib import Path
import logging
import gc
import time
import shutil
import requests

def get_all_files(directory):
    """
    遍历指定目录，获取所有文件的相对路径。
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        # 计算相对于指定目录的路径
        rel_root = os.path.relpath(root, directory)
        for file in files:
            if rel_root == '.':
                rel_path = file
            else:
                rel_path = os.path.join(rel_root, file)
            file_list.append(rel_path)
    return file_list

def filter_ignored_files(directory, match_rule):
    """
    过滤出被 .gitignore 规则忽略的文件。
    """
    spec = pathspec.PathSpec.from_lines('gitwildmatch', match_rule)
    all_files = get_all_files(directory)
    ignored_files = spec.match_files(all_files)
    return [file for file in ignored_files]

class GitFileRetriever:
    def __init__(self, repo_path):
        """
        初始化 Git 仓库访问器
        
        Args:
            repo_path (str): Git 仓库的本地路径
        """
        self.repo_path = Path(repo_path)
        self.logger = self._setup_logger()
        
        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            self.logger.error(f"'{repo_path}' 不是有效的 Git 仓库")
            raise
        except Exception as e:
            self.logger.error(f"初始化 Git 仓库时发生错误: {str(e)}")
            raise
        self.largest_commit = self.repo.head.commit.hexsha

    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    # 在 GitFileRetriever 类中修改 get_file_content 方法
    def get_file_content(self, file_path, commit_hash):
        """
        获取指定 commit 之后文件的状态
        
        Args:
            file_path (str): 文件相对路径
            commit_hash (str): commit 的哈希值
            
        Returns:
            str: 文件内容
        """
        try:
            # 确保文件路径是相对于仓库根目录的
            relative_path = Path(file_path).relative_to(self.repo_path) if Path(file_path).is_absolute() else Path(file_path)
            file_path_str = str(relative_path).replace('\\', '/')  # 统一使用正斜杠
            
            # 获取指定的 commit
            commit = self.repo.commit(commit_hash)
            # self.logger.info(f"获取 commit: {commit_hash[:8]} - {commit.message.strip()}")

            try:
                # 首先尝试直接从该 commit 获取文件
                blob = commit.tree / file_path_str
                return blob.data_stream.read().decode('utf-8')
            except KeyError:
                # 如果在当前 commit 中没找到，则获取该文件最后一次修改的内容
                for past_commit in self.repo.iter_commits(commit_hash, paths=file_path_str):
                    try:
                        blob = past_commit.tree / file_path_str
                        # self.logger.info(f"文件内容来自之前的 commit: {past_commit.hexsha[:8]}")
                        return blob.data_stream.read().decode('utf-8')
                    except KeyError:
                        continue
                
                # 如果在历史记录中都找不到该文件
                raise KeyError(f"在仓库历史中未找到文件: {file_path_str}")

        except git.exc.BadName:
            self.logger.error(f"无效的 commit hash: {commit_hash}")
            raise
        except KeyError as e:
            self.logger.error(f"文件未找到: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"获取文件内容时发生错误: {str(e)}")
            raise
    def get_file_diff(self, file_path, commit_hash1, commit_hash2=None):
        """
        获取指定文件在两个 commit 之间的差异
        
        Args:
            file_path (str): 文件相对路径
            commit_hash1 (str): 第一个 commit 的哈希值
            commit_hash2 (str): 第二个 commit 的哈希值
            
        Returns:
            str: 文件差异内容
        """
        try:
            # 确保文件路径是相对于仓库根目录的
            if commit_hash2 is None:
                commit_hash2 = self.largest_commit
            relative_path = Path(file_path).relative_to(self.repo_path) if Path(file_path).is_absolute() else Path(file_path)
            file_path_str = str(relative_path).replace('\\', '/')  # 统一使用正斜杠
            
            # 获取两个指定的 commit
            commit1 = self.repo.commit(commit_hash1)
            commit2 = self.repo.commit(commit_hash2)
            
            # 获取差异
            diff = self.repo.git.diff(commit1.hexsha, commit2.hexsha, '--', file_path_str)
            
            if not diff:
                self.logger.info(f"文件 {file_path_str} 在这两个 commit 之间没有变化")
                return ""
                
            return diff
            
        except git.exc.BadName as e:
            self.logger.error(f"无效的 commit hash: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"获取文件差异时发生错误: {str(e)}")
            raise

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器时自动清理"""
        self.close()
        
    def close(self):
        """更彻底地清理和释放资源"""
        try:
            if hasattr(self, 'repo'):
                # 关闭所有文件句柄
                if self.repo.git.git is not None:
                    if hasattr(self.repo.git.git, '_handle'):
                        self.repo.git.git._handle.close()
                
                # 清理 git 命令运行器
                if hasattr(self.repo, 'git'):
                    del self.repo.git
                
                # 关闭仓库
                self.repo.close()
                
                # 删除仓库引用
                del self.repo
                
                # 强制垃圾回收
                gc.collect()
                
                # 在 Windows 上可能需要短暂等待
                time.sleep(0.1)
                
                self.logger.info("Git 仓库资源已释放")
        except Exception as e:
            self.logger.error(f"关闭仓库时发生错误: {str(e)}")

    def __del__(self):
        """析构函数中确保资源被释放"""
        self.close()

def cleanup_directory(directory):
    """安全地清理目录"""
    max_retries = 3
    retry_delay = 1  # 秒

    for attempt in range(max_retries):
        try:
            # 强制运行垃圾回收
            gc.collect()
            
            # 在 Windows 上，遍历删除只读属性
            for root, dirs, files in os.walk(directory):
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    os.chmod(dir_path, 0o777)
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, 0o777)
            
            # 删除目录
            shutil.rmtree(directory)
            break
        except PermissionError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)
            continue

def create_github_issue(repo_id, title, body, token):
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo_id}/issues"
    
    # 设置请求头
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # issue的数据
    data = {
        "title": title,
        "body": body
    }
    
    # 发送POST请求
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Issue创建成功！")
        return response.json()
    else:
        print(f"创建失败，状态码: {response.status_code}")
        print(response.text)
        return None

def diff_format(diff:dict):
    markdown_text=''
    for key in diff:
        markdown_text=markdown_text+f'### {key} \n'
        markdown_text=markdown_text+f'```diff \n{diff[key]} \n``` \n'
    return markdown_text