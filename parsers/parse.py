from __future__ import print_function
import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parser'))
sys.path.append(os.path.join(project_path, 'parsers'))

import pdb
import argparse
from pycparser import parse_file, c_generator
from pathlib import Path

from parsers import Extractor, remove_comments, repo_parser
from funcs_extract_ast import FuncDefVisitor, FuncCallVisitor
from files_handler import save_pkl, load_file, save_file
from config import basic_fake_headers_path


def func_export(ast):
    func_def = FuncDefVisitor(ast)
    nodes = func_def.funcdefs
    func_call = FuncCallVisitor(nodes)
    funcs = func_call.func_calls
    return funcs


def save(ast_file, code, re_gen, save_dir):
    if re_gen:
        generator = c_generator.CGenerator()
        with open(f'/{save_dir}/re_code.c', 'w') as f:
            f.write(generator.visit(list(ast_file)[-1]))
    save_file(code, os.path.join(save_dir, 'code.c'))
    save_pkl(ast_file, os.path.join(save_dir, 'ast'))


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


def fake_main_handler(code):
    code = remove_comments(code)
    code = code.strip()

    return code


def ast(origin_folder, fake_headers_path, save_dir, re_gen=False):
    """
    Get the AST representation of the main file in the origin folder.
    Save the AST file and the source code without comments.
    Regenerate c from AST if re_gen is True.
    """
    mains, real_headers, c_files = repo_parser(repo_dir=origin_folder, with_ext=True)
    main_path, main_name = list(mains.keys())[0], list(mains.values())[0]

    code, _, _ = load_file(main_path, load_by_line=False)
    code = fake_main_handler(code)
    fake_headers_handler(fake_headers_path, real_headers, main_path)

    program_dirs = [f'-I{os.path.join(root, dir)}' for (root, dirs, fnames) in os.walk(origin_folder) for dir in dirs]
    cpp_args = ["-E"] + ["-D__attribute__(x)="] + [f'-I{origin_folder}'] + program_dirs + [f"-I{basic_fake_headers_path}"] + [f"-I{fake_headers_path}"]
    ast_file = parse_file(main_path, use_cpp=True, cpp_path='mpicc', cpp_args=cpp_args)
    save(ast_file, code, re_gen, save_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='origin_folder', type=str, nargs='?', default=r'/home/nadavsc/LIGHTBITS/code2mpi/ast_parse/test_loop', help="Path of the folder of the targeted file")
    parser.add_argument(dest='fake_headers_path', type=str, nargs='?', default='', help="Path to create fake headers")
    parser.add_argument(dest='save_dir', type=str, default='', nargs='?', help="Path to save the outputs")
    parser.add_argument('-re_gen', '--re_gen', action='store_true', help="Regenerate c from AST")

    args = parser.parse_args()
    origin_folder = args.origin_folder
    fake_headers_path = args.fake_headers_path
    save_dir = args.save_dir
    re_gen = args.re_gen

    if fake_headers_path == '' or save_dir == '':
        fake_headers_path = origin_folder
        save_dir = origin_folder
    ast(origin_folder=origin_folder,
        fake_headers_path=fake_headers_path,
        save_dir=save_dir,
        re_gen=re_gen)

# mpicc -E -D'__attribute__(x)=' -Itest/lemon/check -Ipycparser/utils/fake_libc_include test/lemon/check/lemon_benchmark.c  > lemon_benchmark_pp.c