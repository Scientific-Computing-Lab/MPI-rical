import os
import re
import json
import collections
import matplotlib.pyplot as plt

from repository import Repo
from repos_parser import REPOS_ORIGIN_DIR, REPOS_MPI_DIR, EXTENSIONS, FORTRAN_EXTENSIONS
from repos_parser import write_to_json, get_extension


class Database:
    def __init__(self, database_path=None):
        if database_path:
            self.database = self.load_database(database_path)
        else:
            self.write_database_json()

    def write_database_json(self):
        database_info = {}
        for idx, repo_name in enumerate(os.listdir(REPOS_MPI_DIR)):
            repo = Repo(repo_name=repo_name,
                        repos_dir=REPOS_MPI_DIR,
                        idx=idx,
                        copy=False)
            repo.scan_repo()
            database_info[repo_name] = repo.repo_info[repo_name]
        write_to_json(database_info, 'database.json')

    def load_database(self, path):
        with open(path, 'r') as f:
            return json.load(f)

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

database = Database('database.json')
total_functions = database.total_functions()
database.set_counter()
print('YADA')
