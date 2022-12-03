import os

from repos_parser import REPOS_ORIGIN_DIR, name_split
from script import Script

from pycparser import parse_file


def main_programs(main_fname, script, repo_headers, headers=[]):
    include_headers = script.get_headers()
    for header in include_headers:
        if header in repo_headers.keys():
            headers += main_programs(main_fname, Script(path=repo_headers[header]), repo_headers, headers)
    if script.fname != main_fname:
        return [script.fname]
    return headers


def get_repo_headers(repos_dir, repo_name):
    headers = {}
    repo_dir = os.path.join(repos_dir, repo_name)
    for idx, (root, dirs, files) in enumerate(os.walk(repo_dir)):
        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext == '.h':
                headers[file_name] = os.path.join(root, file_name)
    return headers


def get_main(repos_dir, repo_name):
    main = {}
    for idx, (root, dirs, files) in enumerate(os.walk(os.path.join(repos_dir, repo_name))):
        for fname in files:
            _, ext = name_split(fname)
            if ext == '.c':
                path = os.path.join(root, fname)
                script = Script(path, load_by_line=False)
                if script.is_main():
                    main[path] = fname
    return main


repo_headers = get_repo_headers(repos_dir=REPOS_ORIGIN_DIR,
                                repo_name='ADCDS')
main = get_main(repos_dir=REPOS_ORIGIN_DIR,
                repo_name='ADCDS')
# headers = main_programs('png_manager_test.c',
#                         Script(path=r'/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos/ADCDS/MPI_CountingStars/Tests/png_manager_test.c'),
#                         repo_headers)
headers = main_programs('main.c',
                        Script(path=r'/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos/ADCDS/MPI_CountingStars/main.c'),
                        repo_headers)
print(headers)
print('YADA')