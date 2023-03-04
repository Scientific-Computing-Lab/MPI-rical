import os
import re
import pdb

from files_parser import load_file, name_split, space_remove
from repos_parser import load_json

from pycparser import parse_file


def match_funcs(pre_funcs, funcs):
    for pre_func in pre_funcs:
        for func in funcs:
            start_pre_func = function_starter(pre_func)
            start_func = function_starter(func)
            if start_pre_func and start_func:
                if start_pre_func[0] == start_func[0]:
                    return True
    return False


def database_functions_parser(functions_db, repo_path, headers_path):
    couples = []
    files = functions_db[repo_path]['files']
    if not files:
        return couples
    headers_path = [h_path for h_path in headers_path if h_path in list(files.keys())]
    for h_path in headers_path:
        for f_path, functions in files.items():
            if os.path.splitext(f_path)[-1] == '.c':
                if match_funcs(files[h_path]['functions'], functions['functions']):
                    couples.append(f_path)
    return list(set(couples))


def is_main(lines):
    if re.search(r'int main[(](.*?)[)]', lines, flags=re.IGNORECASE):
        return True


def include_headers(path, real_headers, exclude_headers, all_headers=[]):
    lines = load_file(path, load_by_line=False)
    headers = [header for header in re.findall(f'#include[\s]*[<"](.*?)[">]', str(lines), flags=re.IGNORECASE)]
    if not headers and os.path.basename(path) not in real_headers and not path.endswith('.c'):
        all_headers.append(os.path.basename(path))
        return all_headers

    for header in headers:
        if header in real_headers:
            include_headers(real_headers[header], real_headers, exclude_headers, all_headers)
        elif header not in exclude_headers and not path.endswith('.c'):
            all_headers.append(header)
    return list(set(all_headers))


def file_headers(path):
    lines = load_file(path, load_by_line=False)
    headers = [header for header in re.findall(f'#include[\s]*[<"](.*?)[">]', str(lines), flags=re.IGNORECASE)]
    return os.path.basename(path), headers


class Extractor:
    def __init__(self, main_path, main_name, repo_headers):
        self.headers = []
        self.main_path = main_path
        self.main_name = main_name
        self.repo_headers = repo_headers

    def extraction(self, file_path):
        if file_path in self.headers:
            return

        script_name, include_headers = file_headers(file_path)
        if script_name != self.main_name:
            self.headers.append(file_path)

        for header in include_headers:
            if header in self.repo_headers.keys():
                self.extraction(self.repo_headers[header])

    def c_files(self, function_db, repo_dir, headers_path):
        return database_functions_parser(function_db, repo_dir, headers_path)


def repo_parser(repos_dir, repo_name, find_headers=True, find_main=True):
    headers = {}
    mains = {}
    repo_path = os.path.join(repos_dir, repo_name)
    for idx, (root, dirs, files) in enumerate(os.walk(repo_path)):
        for fname in files:
            _, ext = name_split(fname)
            if find_headers:
                if ext == '.h':
                    headers[fname] = os.path.join(root, fname)
            if find_main:
                if ext == '.c':
                    path = os.path.join(root, fname)
                    lines, _, _ = load_file(path, load_by_line=False)
                    if is_main(lines):
                        mains[path] = fname
    return mains, headers


def functions_implementations(lines):
    return re.findall(r'[a-z]*\s[a-z*]*[(](.*?)[)]\s{', lines, flags=re.IGNORECASE)


def functions_in_header(lines):
    return [space_remove(match.group()) for match in re.finditer(r'[\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[(]', lines, flags=re.IGNORECASE)]
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s[a-z0-9_*\\]*\s*[(]
# [\\][n][a-z0-9_*]+\s[a-z0-9_*]+\s[a-z0-9_*]*\s*[(]
# [\\][n][a-z0-9*]*\s[a-z0-9_*]*[(](.*?)[)];
# \\n\s*(?:[\w\*]+\s+)?\w+\s*\([^;]*\)\s*(?:const)?\s*(?:[^;]*;)


def prefix_include(lines):
    return list(re.finditer(r'^if[\s(]', lines, flags=re.IGNORECASE)) + \
           list(re.finditer(r'^else[\s(]', lines, flags=re.IGNORECASE)) + \
           list(re.finditer(r'^case[\s]', lines, flags=re.IGNORECASE))


def functions_in_c(lines):
    return [space_remove(match.group()) for match in re.finditer(r'[\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[^{(;]*\([^)]*\)[^{;]*{', lines, flags=re.IGNORECASE)]
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[^(;]*\([^)]*\)[^{;]*{
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[^(]*\([^)]*\)[^{;]*{
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[(](.*?)[)]([\\][n])*\s*[{]
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[{]


def functions_in_file(lines, ext):
    functions = functions_in_c(lines)
    if ext == '.h':
        functions += functions_in_header(lines)
    return [func for func in functions if len(func) < 350 and not prefix_include(func)]


def function_starter(function):
    return [space_remove(match.group()) for match in re.finditer(r'[a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[({]', function, flags=re.IGNORECASE)]