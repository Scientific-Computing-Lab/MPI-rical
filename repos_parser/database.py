import os
import re
import json
import collections
import matplotlib.pyplot as plt

from user import User
from repos_parser import REPOS_ORIGIN_DIR, REPOS_MPI_DIR, REPOS_MPI_SLICED_DIR, EXTENSIONS, FORTRAN_EXTENSIONS
from repos_parser import write_to_json, load_json, name_split
from c_parse import main_division, repo_parser
from script import Script


class Database:
    def __init__(self, repos_dir, new_db_name=None, database_path=None):
        self.database = {}
        self.repos_dir = repos_dir
        if database_path:
            self.database = load_json(database_path)
        else:
            self.create_database(new_db_name)

    def load_users(self):
        for idx, user_name in enumerate(os.listdir(self.users_dir)):
            yield User(user_name=user_name,
                       users_dir=self.users_dir,
                       idx=idx,
                       copy=False)

    def create_database(self, new_db_name):
        for user in self.load_users():
            user.scan_user()
            if user.included:
                self.database[user.name] = user.json_user_info[user.name]
        write_to_json(self.database, f'{new_db_name}.json')

    def program_division(self):
        self.programs = []
        mains, repo_headers = repo_parser(self.repos_dir, self.name)
        for main_path, main_name in mains.items():
            program = {'main': {'path': main_path, 'name': main_name}, 'headers': {}}
            headers_path = main_division(main_name, Script(main_path), repo_headers)
            program['headers'] = headers_path

    def functions_chain_counter(self):
        chain_funcs = {}
        for user_name, info in self.database.items():
            for script_name, script_info in info['scripts'].items():
                funcs = '->'.join(script_info['funcs'].keys()).lower()
                chain_funcs[funcs] = (chain_funcs[funcs] if funcs in chain_funcs else 0) + 1
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
        if name_split(fname)[1] in EXTENSIONS:
            return re.search('_slice', fname)
        return True

    def clear(self):
        for (root, dirs, fnames) in os.walk(REPOS_MPI_DIR):
            for fname in fnames:
                if self.is_remove(fname):
                    os.remove(os.path.join(root, fname))


database = Database(repos_dir=REPOS_MPI_SLICED_DIR,
                    new_db_name=None,
                    database_path='database_sliced.json')
database.functions_chain_counter()
print('YADA')