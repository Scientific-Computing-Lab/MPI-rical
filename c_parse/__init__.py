import os
import re

from files_parser import name_split, is_main, load_file, file_headers

from pycparser import parse_file


def repo_parser(repos_dir, repo_name, find_headers=True, find_main=True):
    headers = {}
    mains = {}
    for idx, (root, dirs, files) in enumerate(os.walk(os.path.join(repos_dir, repo_name))):
        for fname in files:
            _, ext = name_split(fname)
            if find_headers:
                if ext == '.h':
                    headers[fname] = os.path.join(root, fname)
            if find_main:
                if ext == '.c':
                    path = os.path.join(root, fname)
                    lines = load_file(path, load_by_line=False)
                    if is_main(lines):
                        mains[path] = fname
    return mains, headers

## TODO: add .c extractors
class Extractor:
    def __init__(self, main_fname, repo_headers):
        self.headers = []
        self.main_fname = main_fname
        self.repo_headers = repo_headers

    def extraction(self, file_path):
        if file_path in self.headers:
            return

        script_name, include_headers = file_headers(file_path)
        if script_name != self.main_fname:
            self.headers.append(file_path)

        for header in include_headers:
            if header in self.repo_headers.keys():
                self.extraction(self.repo_headers[header])


# def main_division(main_fname, script_path, repo_headers, headers=[]):
#     script_name, include_headers = file_details(script_path)
#     for header in include_headers:
#         if header in repo_headers.keys():
#             headers += main_division(main_fname, repo_headers[header], repo_headers, headers)
#     if script_name != main_fname:
#         return [script_path]
#     return headers

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