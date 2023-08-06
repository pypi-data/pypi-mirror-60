import subprocess
import os
from click import get_app_dir
import json

class Gitcd():
    def __init__(self, index_file=None):
        self.repo_index = {}
        self.index_file = index_file if index_file else os.path.join(get_app_dir("gitcd"), "repo_index.json")

    def get_repo_index(self):
        return self.repo_index

    def get_repo_name_list(self):
        return [k for k in self.repo_index.keys()]

    def get_repo_dir(self, repo_name):
        try:
            return self.repo_index[repo_name]
        except:
            return None
    
    def get_index_file_path(self):
        return self.index_file
    
    def set_index_path_file_path(self, file_path):
        self.index_file = os.path.abspath(os.path.expanduser(file_path))

    def read_repo_index(self):
        if not os.path.exists(self.index_file):
            return False

        with open(self.index_file, "r") as file:
            self.repo_index = json.load(file)

        return True

    def write_repo_index(self):
        index_dir = os.path.dirname(self.index_file)
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)

        with open(self.index_file, "w") as file:
            json.dump(self.repo_index, file, indent=4)

    def generate_repo_index(self, path="~"):
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            return False

        for root, path, _ in os.walk(path):
            if ".git" in path:
                self.repo_index[os.path.basename(root)] = root

        return True

    def update_repo_index(self):
        deleted_repo = [repo for repo in self.repo_index if not os.path.exists(os.path.join(repo, ".git"))]
        for repo in deleted_repo: del self.repo_index[repo]