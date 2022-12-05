import multiprocessing as mp
import os
import re
import gc

from repos_parser import name_split, copy_file, script_types, start_idx_calc, src_dst_prep, load_json
from repos_parser import EXTENSIONS, FORTRAN_EXTENSIONS, REPOS_ORIGIN_DIR, REPOS_MPI_DIR, PROGRAMS_MPI_DIR, REPOS_MPI_SLICED_DIR
from script import Script
from program import Program
from c_parse import repo_parser, main_division, script_details

from multiprocessing import Pool
from logger import set_logger, info


class User:
    def __init__(self, user_name, users_dir, idx=0, copy=False):
        self.name = user_name
        self.users_dir = users_dir
        self.idx = idx
        self.copy = copy

        self.user_dir = os.path.join(users_dir, user_name)
        self.scripts = None
        self.included = False
        self.repos = self.get_repos()
        self.json_structure_init()

    def get_repos(self):
        return {repo_name: os.path.join(self.user_dir, repo_name) for repo_name in os.listdir(self.user_dir)}

    def json_structure_init(self):
        self.json_user_info = {self.name: {'types': {}, 'scripts': {}}}
        self.json_user_types = self.json_user_info[self.name]['types']
        self.json_user_scripts = self.json_user_info[self.name]['scripts']

    def update_counters(self, ext):
        self.json_user_types[ext] = (self.json_user_types[ext] if ext in self.json_user_types else 0) + 1
        script_types[ext] = (script_types[ext] if ext in script_types else 0) + 1

    def update_json(self, fname, funcs_counter):
        self.json_user_scripts[fname] = {'funcs': {}}
        self.json_user_scripts[fname]['funcs'] = funcs_counter

    def load_scripts(self):
        for idx, (root, dirs, fnames) in enumerate(os.walk(self.user_dir)):
            for fname in fnames:
                if name_split(fname)[1] in EXTENSIONS:
                    yield Script(fname, os.path.join(root, fname))

    def scan_user(self):
        for script in self.load_scripts():
            if script.funcs_counter:
                self.included = True
                self.update_counters(script.ext)
                self.update_json(script.fname, script.funcs_counter)
                if self.copy:
                    copy_file(src=script.path, dst=REPOS_MPI_DIR, src_origin=REPOS_ORIGIN_DIR)
                break
        print(f'{self.idx}) {script_types}')

    def init_final_slice(self):
        sliced = False
        for idx, (root, dirs, fnames) in enumerate(os.walk(self.user_dir)):
            self.scripts = [Script(os.path.join(root, fname), False) for fname in fnames if name_split(fname)[1] in EXTENSIONS]
            for script in self.scripts:
                _, dst = src_dst_prep(script.path, REPOS_MPI_SLICED_DIR, REPOS_MPI_DIR)
                script_sliced = script.init_final_slice(dst)
                if script_sliced:
                    sliced = True
        if sliced:
            info(f'{self.idx}) {self.name} has been SLICED')

    # def f(self, item):
    #     repo_name, repo_dir = item
    #     self.programs_user_dir = os.path.join(PROGRAMS_MPI_DIR, self.name)
    #     mains, repo_headers = repo_parser(self.users_dir, repo_dir)
    #     if mains and not os.path.exists(self.programs_user_dir):
    #         os.makedirs(self.programs_user_dir)
    #     for main_path, main_name in mains.items():
    #         program = {'main': {'path': main_path, 'name': main_name}, 'headers': {}}
    #         headers_path = main_division(main_name, main_path, repo_headers, headers=[])
    #         program['headers'] = headers_path
    #         Program(program=program, user=self, repo_name=repo_name, repo_dir=repo_dir)
    #
    # def program_division(self):
    #     with Pool(mp.cpu_count()) as p:
    #         p.map(self.f, self.repos.items())

    def main_division(self, main_fname, script_path, repo_headers):
        script_name, include_headers = script_details(script_path)
        for header in include_headers:
            if header in repo_headers.keys():
                self.headers_path += self.main_division(main_fname, repo_headers[header], repo_headers)
        if script_name != main_fname:
            return [script_path]

    def copy_files(self, main_path, repo_dir):
        copy_file(src=main_path, dst=self.program_path, src_origin=repo_dir)
        for header_path in self.headers_path:
            copy_file(src=header_path, dst=self.program_path, src_origin=repo_dir)
        info(f'PROGRAM {self.id} has been created - Origin repo: {self.name}')

    def init_folder(self):
        if not os.path.exists(self.programs_repo_dir):
            os.makedirs(self.programs_repo_dir)
        programs_names = os.listdir(self.programs_repo_dir)
        if programs_names:
            id = int(programs_names[-1].split('_')[1]) + 1
        else:
            id = 0
        path = os.path.join(os.path.join(self.programs_repo_dir, f'program_{id}'))
        os.makedirs(path)
        return id, path

    def program_division(self):
        for repo_name, repo_dir in self.repos.items():
            self.programs_user_dir = os.path.join(PROGRAMS_MPI_DIR, self.name)
            self.programs_repo_dir = os.path.join(self.programs_user_dir, repo_name)
            mains, repo_headers = repo_parser(self.users_dir, repo_dir)
            if mains and not os.path.exists(self.programs_user_dir):
                os.makedirs(self.programs_user_dir)
            for main_path, main_name in mains.items():
                self.headers_path = []
                self.main_division(main_name, main_path, repo_headers)
                self.id, self.program_path = self.init_folder()
                self.copy_files(main_path, repo_dir)
