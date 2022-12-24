import os
import re

from files_parser import load_file, name_split

from pycparser import parse_file


def is_main(lines):
    if re.search(r'int main[(](.*?)[)]', lines, flags=re.IGNORECASE):
        return True


def file_headers(path):
    lines = load_file(path, load_by_line=False)
    headers = [f'{header}.h' for header in re.findall(f'[<"](.*?).h[">]', str(lines), flags=re.IGNORECASE)]
    return os.path.basename(path), [header.split('/')[-1] for header in headers]


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
                    lines, _, _ = load_file(path, load_by_line=False)
                    if is_main(lines):
                        mains[path] = fname
    return mains, headers


def functions_implementations(lines):
    return re.findall(r'[a-z]*\s[a-z*]*[(](.*?)[)]\s{', lines, flags=re.IGNORECASE)


def functions_in_header(lines):
    return [lines[slice(*match.span())] for match in re.finditer(r'[\\][n][a-z]*\s[a-z0-9_]*[(](.*?)[)];', lines, flags=re.IGNORECASE)]