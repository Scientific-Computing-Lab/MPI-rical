import os
import re

from files_parser import load_file
from config import exclude_headers


def extract_headers(path):
    lines, _, _ = load_file(path, load_by_line=False)
    headers = [header for header in re.findall(f'#[\s]*include[\s]*[<"](.*?)[">]', str(lines), flags=re.IGNORECASE)]
    return os.path.basename(path), headers


class Extractor:
    def __init__(self, real_headers, main_path='', main_name=''):
        self.headers = {}
        self.fake_headers = []
        self.headers_path = []
        self.visit_headers = []
        self.main_path = main_path
        self.main_name = main_name
        self.real_headers = real_headers

    def extraction(self, file_path):
        if file_path in self.headers_path:
            return

        script_name, include_headers = extract_headers(file_path)
        if script_name != self.main_name:
            self.headers_path.append(file_path)

        for header in include_headers:
            if header in self.real_headers.keys():
                self.extraction(self.real_headers[header])

    def is_real(self, fname):
        for path in self.real_headers.keys():
            if path[-len(fname):] == fname and os.path.basename(path) == fname:
                return path
        return None

    def path_match(self, headers_names):
        headers = {}
        for fname in headers_names:
            if self.real_headers:
                path = self.is_real(fname)
                if path:
                    headers[path] = fname
                elif fname not in exclude_headers:
                    self.fake_headers.append(fname)
        return headers

    def include_headers(self, path):
        self.visit_headers.append(path)
        _, headers_names = extract_headers(path)
        headers = self.path_match(headers_names)

        for header_path, header_name in headers.items():
            if header_path not in self.visit_headers:
                if header_path in self.real_headers:
                    self.include_headers(header_path)
        return list(set(self.fake_headers))