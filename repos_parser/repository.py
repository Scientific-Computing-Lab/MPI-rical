import os
import re

from repos_parser import get_extension, copy_file, script_types, start_idx_calc, src_dst_prep
from repos_parser import EXTENSIONS, FORTRAN_EXTENSIONS, REPOS_MPI_DIR, REPOS_MPI_SLICED_DIR, REPOS_ORIGIN_DIR
from script import Script

from logger import set_logger, info


class Repo:
    def __init__(self, repo_name, repos_dir, idx, copy=False):
        self.repo_name = repo_name
        self.repos_dir = repos_dir
        self.copy = copy
        self.idx = idx
        self.scripts = None

        self.root_dir = os.path.join(repos_dir, repo_name)
        self.json_structure_init()
        self.included = False

    def json_structure_init(self):
        self.json_repo_info = {self.repo_name: {'types': {}, 'scripts': {}}}
        self.json_repo_types = self.json_repo_info[self.repo_name]['types']
        self.json_repo_scripts = self.json_repo_info[self.repo_name]['scripts']

    def update_counters(self, ext):
        self.json_repo_types[ext] = (self.json_repo_types[ext] if ext in self.json_repo_types else 0) + 1
        script_types[ext] = (script_types[ext] if ext in script_types else 0) + 1

    def update_json(self, fname, funcs_counter):
        self.json_repo_scripts[fname] = {'funcs': {}}
        self.json_repo_scripts[fname]['funcs'] = funcs_counter

    def scan_repo(self):
        for idx, (root, dirs, fnames) in enumerate(os.walk(self.root_dir)):
            self.scripts = [Script(fname, os.path.join(root, fname)) for fname in fnames if get_extension(fname) in EXTENSIONS]
            for script in self.scripts:
                if script.funcs_counter:
                    self.included = True
                    self.update_counters(script.ext)
                    self.update_json(script.fname, script.funcs_counter)
                    if self.copy:
                        copy_file(src=script.path, dst=REPOS_MPI_DIR, src_repo=REPOS_ORIGIN_DIR, MPI_functions=script.funcs_counter)
                    break
        print(f'{self.idx}) {script_types}')

    def init_final_slice(self):
        if self.repo_name == 'hpc':
            print('YADA')
        sliced = False
        for idx, (root, dirs, fnames) in enumerate(os.walk(self.root_dir)):
            self.scripts = [Script(fname, os.path.join(root, fname), False) for fname in fnames if get_extension(fname) in EXTENSIONS]
            for script in self.scripts:
                _, dst = src_dst_prep(script.path, REPOS_MPI_SLICED_DIR, REPOS_MPI_DIR)
                script_sliced = script.init_final_slice(dst)
                if script_sliced:
                    sliced = True
        if sliced:
            info(f'{self.idx}) {self.repo_name} has been SLICED')