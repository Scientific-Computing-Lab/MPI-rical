from __future__ import print_function
import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'repos_parser'))
sys.path.append(os.path.join(project_path, 'files_parser'))
sys.path.append(os.path.join(project_path, 'c_parse'))
sys.path.append(os.path.join(project_path, 'parsers'))

import pdb
import shutil
from pycparser import parse_file
from pathlib import Path

from c_parse import replace_headers_ext, repo_parser, Extractor, remove_comments
from func_visitors import FuncDefVisitor, FuncCallVisitor
from files_parser import load_file
from config import exclude_headers


def func_export(ast):
    func_def = FuncDefVisitor(ast)
    nodes = func_def.funcdefs
    func_call = FuncCallVisitor(nodes)
    funcs = func_call.func_calls
    return funcs


def write_fake_code(code, fake_code_path, c_files_headers):
    for c_file_header in c_files_headers:
        shutil.copy(src=real_headers[f'{c_file_header[:-2]}'], dst=os.path.join(fake_code_path, c_file_header))
    with open(os.path.join(fake_code_path, os.path.basename(file_path)), 'w') as f:
        f.write(code)


def fake_code_handler(repo_dir, mains, real_headers, c_files):
    fake_code_path = os.path.join(repo_dir, 'fake_code')
    try:
        os.mkdir(fake_code_path)
    except:
        print('Fake code path is already exists...')
    files_paths = [c_path for c_name, c_path in c_files.items()
                   for h_name, h_path in real_headers.items() if c_name == h_name]
    files_paths += mains.values()

    for file_path in files_paths:
        lines, _, _ = load_file(file_path, load_by_line=False)
        code, c_files_headers = replace_headers_ext(lines, real_headers)
        write_fake_code(code, fake_code_path, c_files_headers)


def fake_headers_handler(fake_headers_path, repo_headers, file_path):
    extractor = Extractor(real_headers=repo_headers)
    headers = extractor.include_headers(path=file_path, name=os.path.basename(file_path))

    headers_paths = []
    for header_name in headers.values():
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
    origin_folder = r"/home/nadavsc/LIGHTBITS/code2mpi/c_parse/test/lemon"
    file_path = r"/home/nadavsc/LIGHTBITS/code2mpi/c_parse/test/lemon/fake_code/lemon_benchmark.c"

    fake_headers_path = os.path.join(origin_folder, 'fake_headers')
    basic_fake_headers_path = r"/home/nadavsc/LIGHTBITS/code2mpi/c_parse/pycparser/utils/fake_libc_include"
    mains, real_headers, c_files = repo_parser(repo_dir=origin_folder, with_ext=False)

    fake_code_handler(origin_folder, mains, real_headers, c_files)
    fake_headers_handler(fake_headers_path, real_headers, file_path)
    pdb.set_trace()
    program_dirs = [f'-I{os.path.join(root, dir)}' for (root, dirs, fnames) in os.walk(origin_folder) for dir in dirs]
    cpp_args = ["-E"] + ["-D__attribute__(x)="] + [f'-I{origin_folder}'] + program_dirs + [f"-I{basic_fake_headers_path}"] + [f"-I{fake_headers_path}"]
    ast = parse_file(file_path, use_cpp=True, cpp_path='mpicc', cpp_args=cpp_args)
    pdb.set_trace()
    print(func_export(ast))

# mpicc -E -D'__attribute__(x)=' -Itest/lemon/check -Ipycparser/utils/fake_libc_include test/lemon/check/lemon_benchmark.c  > lemon_benchmark_pp.c