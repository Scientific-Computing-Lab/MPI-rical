import os
import json
import re
import shutil

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
EXTENSIONS = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
FORTRAN_EXTENSIONS = ['.f', '.f77', '.f90', '.f95', '.f03']


def write_to_json(data, path):
    with open(os.path.join(path, '.json'), "w") as f:
        json.dump(data, f, indent=4)


def copy_file(src, dst, MPI_functions):
    START_IDX = len(os.path.join(os.getcwd(), dst)) + 1
    src = src[START_IDX:]
    dst = os.path.join(dst, src)
    dstfolder = os.path.dirname(dst)

    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)

    shutil.copy(os.path.join(REPOS_ORIGIN_DIR, src), dst)
    with open(f'{dst}.json', "w") as f:
        json.dump(MPI_functions, f, indent=4)


def MPI_func_included(contents):
    funcs_count = {}
    MPI_funcs = re.findall('MPI_\w*', contents)  # \S* for all the function
    for func in MPI_funcs:
        funcs_count[func] = (funcs_count[func] if func in funcs_count else 0) + 1
    return funcs_count


def MPI_included(line, language='c'):
    line = str(line).lower()
    if language == 'c':
        return '#include' in line and 'mpi.h' in line
    return 'include' in line and 'mpif.h' in line


class Repo:
    def __init__(self, repo_name, repos_dir, copy=False):
        self.repo_name = repo_name
        self.repos_dir = repos_dir
        self.copy = copy

        self.root_dir = os.path.join(repos_dir, repo_name)
        self.json_structure_init()
        self.repo_include = False

    def json_structure_init(self):
        self.repo_info = {self.repo_name: {'types': {}, 'scripts': {}}}
        self.repo_script_types = self.repo_info[self.repo_name]['types']
        self.repo_scripts = self.repo_info[self.repo_name]['scripts']

    def update_type_counter(self, ext):
        self.repo_script_types[ext] = (self.repo_script_types[ext] if ext in self.repo_script_types else 0) + 1

    def scan_repo(self):
        for idx, (root, dirs, files) in enumerate(os.walk(self.root_dir)):
            for file_name in files:
                self.repo_scripts[file_name] = {'funcs': {}}
                extension = os.path.splitext(file_name)[1].lower()
                if extension in EXTENSIONS:
                    path = os.path.join(root, file_name)
                    with open(path, 'rb') as f:
                        contents = str(f.read())

                    MPI_funcs = MPI_func_included(contents)
                    if MPI_funcs:
                        self.repo_include = True
                        if self.copy:
                            copy_file(path, REPOS_MPI_DIR, MPI_funcs)
                        self.update_type_counter(extension)
                        self.repo_scripts[file_name]['funcs'] = MPI_funcs
                        break

            if idx % 10 ** 3 == 0:
                print(f'{idx}) {self.repo_script_types}')
