import os
import json
import re
import shutil
import collections

from datetime import date

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
EXTENSIONS = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
FORTRAN_EXTENSIONS = ['.f', '.f77', '.f90', '.f95', '.f03']
script_types = {}


def write_to_json(data, path):
    if os.path.isfile(path):
        time = date.today().strftime("%m_%d_%y")
        path = re.sub("database\w*", f"database_info_{time}", path)

    with open(f'{path}.json', "w") as f:
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


def is_print_included(line, ext):
    if ext in FORTRAN_EXTENSIONS:
        return 'print' in line
    else:
        return ('printf' in line) or ('cout' in line)


def mpi_func_included(lines, ext='.c'):
    funcs_count = {}
    funcs = []
    for line in lines:
        line = str(line)
        if not is_print_included(line, ext):
            funcs += re.findall('MPI_\w*', line)  # \S* for all the function
    for func in funcs:
        funcs_count[func] = (funcs_count[func] if func in funcs_count else 0) + 1
    return funcs_count


def mpi_included(line, language='c'):
    line = str(line).lower()
    if language == 'c':
        return '#include' in line and 'mpi.h' in line
    return 'include' in line and 'mpif.h' in line


class Database:
    def __init__(self, database_path=None):
        if database_path:
            self.database = self.load_database(database_path)

    def load_database(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def total_script_types(self):
        counter = collections.Counter()
        for value in self.database.values():
            counter.update(value['types'])
        return dict(counter)

    def total_mpi_functions(self):
        counter = collections.Counter()
        for value in self.database.values():
            for script in value['scripts'].values():
                counter.update(script['funcs'])
        return dict(counter)


class Repo:
    def __init__(self, repo_name, repos_dir, copy=False):
        self.repo_name = repo_name
        self.repos_dir = repos_dir
        self.copy = copy

        self.root_dir = os.path.join(repos_dir, repo_name)
        self.json_structure_init()
        self.included = False

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
                        lines = f.readlines()

                    mpi_funcs = mpi_func_included(lines, extension)
                    if mpi_funcs:
                        self.included = True
                        if self.copy:
                            copy_file(path, REPOS_MPI_DIR, mpi_funcs)
                        self.update_type_counter(extension)
                        self.repo_scripts[file_name]['funcs'] = mpi_funcs
                        script_types[extension] = (script_types[extension] if extension in script_types else 0) + 1
                        break

            if idx % 10 ** 3 == 0:
                print(f'{idx}) {script_types}')

    def init_final_slice(self):
        for idx, (root, dirs, files) in enumerate(os.walk(self.root_dir)):
            for file_name in files:
                script_name, extension = os.path.splitext(file_name)
                path = os.path.join(root, file_name)
                with open(path, 'rb') as f:
                    contents = str(f.read())

                match = re.search(r'\b *mpi_init\b.+\bmpi_finalize\b', contents.lower())
                if match:
                    start_idx, end_idx = match.span()
                    contents = contents[start_idx:end_idx]
                    contents = re.sub(r"\\n", "\n", contents)
                    with open(os.path.join(f'{os.path.split(path)[0]}/{script_name}_slice{extension}'), "w") as f:
                        f.write(contents)

