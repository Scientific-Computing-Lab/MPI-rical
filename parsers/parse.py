from __future__ import print_function
import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parser'))
sys.path.append(os.path.join(project_path, 'parsers'))

import pdb
import shutil
from pycparser import parse_file
from pathlib import Path

from parsers import Extractor, remove_comments, repo_parser
from funcs_extract_ast import FuncDefVisitor, FuncCallVisitor
from files_handler import load_file


def func_export(ast):
    func_def = FuncDefVisitor(ast)
    nodes = func_def.funcdefs
    func_call = FuncCallVisitor(nodes)
    funcs = func_call.func_calls
    return funcs


def fake_headers_handler(fake_headers_path, repo_headers, file_path):
    extractor = Extractor(real_headers=repo_headers)
    headers = extractor.include_headers(path=file_path)

    headers_paths = []
    for header_name in headers:
        header_name = header_name[3:] if header_name[:2] == '..' else header_name
        path = os.path.join(fake_headers_path, header_name)
        headers_paths.append(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
    [Path(header_path).touch() for header_path in headers_paths]


def fake_main_handler(code, main_name, save_outputs_dir):
    code = remove_comments(code)
    code = code.strip()

    file_path = os.path.join(save_outputs_dir, f'proc_{main_name}')
    with open(file_path, 'w') as f:
        f.write(code)


def ast(code, main_name, main_path, origin_folder, real_headers, save_outputs_dir, fake_headers_path, basic_fake_headers_path):
    fake_headers_handler(fake_headers_path, real_headers, main_path)
    fake_main_handler(code, main_name, save_outputs_dir)

    program_dirs = [f'-I{os.path.join(root, dir)}' for (root, dirs, fnames) in os.walk(origin_folder) for dir in dirs]
    cpp_args = ["-E"] + ["-D__attribute__(x)="] + [f'-I{origin_folder}'] + program_dirs + [f"-I{basic_fake_headers_path}"] + [f"-I{fake_headers_path}"]
    return parse_file(main_path, use_cpp=True, cpp_path='mpicc', cpp_args=cpp_args)


if __name__ == "__main__":
    origin_folder = r"/home/nadavsc/LIGHTBITS/code2mpi/parsers/test/lemon"
    file_path = r"/home/nadavsc/LIGHTBITS/code2mpi/parsers/test/lemon/check/lemon_benchmark.c"

    fake_headers_path = os.path.join(origin_folder, 'fake_headers')
    basic_fake_headers_path = r"/home/nadavsc/LIGHTBITS/code2mpi/parsers/pycparser/utils/fake_libc_include"
    mains, real_headers, c_files = repo_parser(repo_dir=origin_folder, with_ext=False)
    fake_headers_handler(fake_headers_path, real_headers, file_path)

    program_dirs = [f'-I{os.path.join(root, dir)}' for (root, dirs, fnames) in os.walk(origin_folder) for dir in dirs]
    cpp_args = ["-E"] + ["-D__attribute__(x)="] + [f'-I{origin_folder}'] + program_dirs + [f"-I{basic_fake_headers_path}"] + [f"-I{fake_headers_path}"]
    pdb.set_trace()
    ast = parse_file(file_path, use_cpp=True, cpp_path='mpicc', cpp_args=cpp_args)
    pdb.set_trace()
    print(func_export(ast))

# mpicc -E -D'__attribute__(x)=' -Itest/lemon/check -Ipycparser/utils/fake_libc_include test/lemon/check/lemon_benchmark.c  > lemon_benchmark_pp.c