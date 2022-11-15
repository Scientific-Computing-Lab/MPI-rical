import os
import re

from repos_parser import get_extension, copy_file, mpi_func_included, script_types
from repos_parser import EXTENSIONS, FORTRAN_EXTENSIONS, REPOS_MPI_DIR, REPOS_ORIGIN_DIR


class Repo:
    def __init__(self, repo_name, repos_dir, idx, copy=False):
        self.repo_name = repo_name
        self.repos_dir = repos_dir
        self.copy = copy
        self.idx = idx

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
        for idx, (root, dirs, fnames) in enumerate(os.walk(self.root_dir)):
            for fname in fnames:
                self.repo_scripts[fname] = {'funcs': {}}
                extension = get_extension(fname)
                if extension in EXTENSIONS:
                    path = os.path.join(root, fname)
                    with open(path, 'rb') as f:
                        lines = f.readlines()

                    mpi_funcs = mpi_func_included(lines, extension)
                    if mpi_funcs:
                        self.included = True
                        if self.copy:
                            copy_file(path, REPOS_MPI_DIR, mpi_funcs)
                        self.update_type_counter(extension)
                        self.repo_scripts[fname]['funcs'] = mpi_funcs
                        script_types[extension] = (script_types[extension] if extension in script_types else 0) + 1
                        break
        print(f'{self.idx}) {script_types}')

    def init_final_slice(self):
        for idx, (root, dirs, fnames) in enumerate(os.walk(self.root_dir)):
            for fname in fnames:
                script_name, extension = os.path.splitext(fname)
                path = os.path.join(root, fname)
                with open(path, 'rb') as f:
                    contents = str(f.read())

                match = re.search(r'\b *mpi_init\b.+\bmpi_finalize\b', contents.lower())
                if match:
                    print(f'{fname} matched')
                    start_idx, end_idx = match.span()
                    contents = contents[start_idx:end_idx]
                    contents = re.sub(r"\\n", "\n", contents)
                    with open(os.path.join(f'{os.path.split(path)[0]}/{script_name}_slice{extension}'), "w") as f:
                        f.write(contents)

