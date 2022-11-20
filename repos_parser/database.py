import os
import re
import json
import collections
import matplotlib.pyplot as plt

from repository import Repo
from repos_parser import REPOS_ORIGIN_DIR, REPOS_MPI_DIR, EXTENSIONS, FORTRAN_EXTENSIONS
from repos_parser import write_to_json, get_extension


def load_json_database(path):
    with open(path, 'r') as f:
        return json.load(f)


class Database:
    def __init__(self, repos_dir, database_path=None):
        self.database = {}
        self.repos_dir = repos_dir
        if database_path:
            self.database = load_json_database(database_path)
        else:
            self.create_database()

    def load_repos(self):
        for idx, repo_name in enumerate(os.listdir(self.repos_dir)):
            yield Repo(repo_name=repo_name,
                       repos_dir=self.repos_dir,
                       idx=idx,
                       copy=False)

    def create_database(self):
        for repo in self.load_repos():
            repo.scan_repo()
            if repo.included:
                self.database[repo.name] = repo.json_repo_info[repo.name]
        write_to_json(self.database, 'database.json')

    def set_counter(self):
        set_counter = {'funcs': {}}
        for repo_name, info in self.database.items():
            for script_name, script_info in info['scripts'].items():
                funcs = '-'.join(script_info['funcs'].keys())
                set_counter['funcs'][funcs] = (set_counter['funcs'][funcs] if funcs in set_counter else 0) + 1
        print('YADA')

    def total_script_types(self):
        counter = collections.Counter()
        for value in self.database.values():
            counter.update(value['types'])
        return dict(counter)

    def total_functions(self):
        counter = collections.Counter()
        for value in self.database.values():
            for script in value['scripts'].values():
                counter.update(script['funcs'])
        return dict(counter)

    def sort_total_functions(self):
        return zip(*dict(sorted(self.total_functions.items(), key=lambda item: item[1], reverse=True)).items())

    def draw_functions_hist(self):
        keys, values = self.sort_total_functions()
        fig, ax = plt.subplots(1, 1)
        ax.set_title('Functions Distribution')
        ax.bar(keys[:30], values[:30], color='g')
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.show()

    def is_remove(self, fname):
        if get_extension(fname) in EXTENSIONS:
            return re.search('_slice', fname)
        return True

    def clear(self):
        for (root, dirs, fnames) in os.walk(REPOS_MPI_DIR):
            for fname in fnames:
                if self.is_remove(fname):
                    os.remove(os.path.join(root, fname))

