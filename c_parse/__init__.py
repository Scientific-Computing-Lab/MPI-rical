import os
import re
import pdb

from files_parser import load_file, name_split, space_remove
from repos_parser import load_json

from config import exclude_headers


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


def replace_headers_ext(code, real_headers):
    c_files_headers = []
    headers = [header for header in re.findall(f'#include[\s]*[<"](.*?)[">]', code, flags=re.IGNORECASE)]
    for header in headers:
        if header[:-2] in real_headers:
            code = code.replace(header, f'{header[:-1]}c')
            c_files_headers.append(f'{header[:-1]}c')
    return code, c_files_headers


def file_headers(path):
    lines = load_file(path, load_by_line=False)
    headers = [header for header in re.findall(f'#include[\s]*[<"](.*?)[">]', str(lines), flags=re.IGNORECASE)]
    return os.path.basename(path), headers


class Extractor:
    def __init__(self, real_headers, main_path='', main_name=''):
        self.headers = {}
        self.headers_path = []
        self.visit_headers = []
        self.main_path = main_path
        self.main_name = main_name
        self.real_headers = real_headers

    def extraction(self, file_path):
        if file_path in self.headers_path:
            return

        script_name, include_headers = file_headers(file_path)
        if script_name != self.main_name:
            self.headers_path.append(file_path)

        for header in include_headers:
            if header in self.real_headers.keys():
                self.extraction(self.real_headers[header])

    def c_files(self, function_db, repo_dir, headers_path):
        return database_functions_parser(function_db, repo_dir, headers_path)

    def attach_path(self, path, fnames):
        return dict(zip([os.path.join(path, fname) if fname[:2] != '..' else os.path.join(os.path.dirname(path), fname[3:]) for fname in fnames], fnames))

    def include_headers(self, path, name):
        self.visit_headers.append(path)
        headers = self.attach_path(os.path.dirname(path), file_headers(path)[1])

        if not headers and path not in self.real_headers and not path.endswith('.c'):
            self.headers[path] = name
            return self.headers

        for header_path, header_name in headers.items():
            if header_path not in self.visit_headers:
                if header_path in self.real_headers and header_path:
                    self.include_headers(header_path, header_name)
                elif os.path.basename(header_path) not in exclude_headers and header_path[-2:] != '.c':
                    self.headers[header_path] = header_name
        return self.headers


def repo_parser(repo_dir, with_ext=True):
    mains = {}
    headers = {}
    c_files = {}
    for idx, (root, dirs, files) in enumerate(os.walk(repo_dir)):
        for fname in files:
            origin_name, ext = name_split(fname)
            name = fname if with_ext else origin_name
            path = os.path.join(root, fname)
            if ext == '.h':
                headers[path] = name
            if ext == '.c':
                lines, _, _ = load_file(path, load_by_line=False)
                if is_main(lines):
                    mains[path] = name
                else:
                    c_files[path] = name
    return mains, headers, c_files


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


def remove_block_comments(lines):
    matches = re.findall(r'/\*.*?\*/', lines, re.DOTALL)
    for match in matches:
        lines = lines.replace(match, '')
    return lines


def remove_singleline_comments(lines):
    return re.sub(r'//.*$', '', lines, flags=re.MULTILINE)


def remove_comments(lines):
    lines = remove_block_comments(lines)
    lines = remove_singleline_comments(lines)
    return lines