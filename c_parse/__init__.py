import os

from repos_parser import REPOS_ORIGIN_DIR, name_split
from script import Script

from pycparser import parse_file


def main_division(main_fname, script, repo_headers, headers=[]):
    include_headers = script.get_headers()
    for header in include_headers:
        if header in repo_headers.keys():
            headers += main_division(main_fname, Script(path=repo_headers[header]), repo_headers, headers)
    if script.fname != main_fname:
        return [script.path]
    return headers


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
                    script = Script(path, load_by_line=False)
                    if script.is_main():
                        mains[path] = fname
    return mains, headers


# mains, repo_headers = repo_parser(repos_dir=REPOS_ORIGIN_DIR, repo_name='ADCDS')
# # headers = main_programs('png_manager_test.c',
# #                         Script(path=r'/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos/ADCDS/MPI_CountingStars/Tests/png_manager_test.c'),
# #                         repo_headers)
# headers = main_division('main.c',
#                         Script(path=r'/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos/ADCDS/MPI_CountingStars/main.c'),
#                         repo_headers)
# print(headers)
# print('YADA')