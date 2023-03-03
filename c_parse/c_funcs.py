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
from pycparser import c_ast, parse_file


class FuncCallVisitor(c_ast.NodeVisitor):
    """
    Travels the node and define whether it contains func call in it
    """
    def __init__(self, nodes, verbose=1):
        self.funcdefs = nodes
        self.inner_visitor = FuncCallInnerVisitor(nodes)
        self.verbose = verbose
        self.func_calls = []
        self.visit(self.funcdefs['main'])

    def visit_FuncCall(self, node):
        name = node.name.name
        if name in self.funcdefs.keys():
            self.inner_visitor.reset()
            self.inner_visitor.visit(self.funcdefs[name])
            self.func_calls += self.inner_visitor.func_calls
        else:
            self.func_calls.append(name)
        if self.verbose > 0:
            print(f'INCLASS: {node.name.name}')


class FuncCallInnerVisitor(c_ast.NodeVisitor):
    """
    Travels the node and define whether it contains func call in it
    """
    def __init__(self, nodes, verbose=0):
        self.funcdefs = nodes
        self.verbose = verbose
        self.func_calls = []

    def reset(self):
        self.func_calls = []

    def visit_FuncCall(self, node):
        name = node.name.name
        if name in self.funcdefs.keys():
            self.visit(self.funcdefs[name])
        else:
            self.func_calls.append(name)
        if self.verbose > 0:
            print(f'INCLASS: {node.name.name}')
        self.generic_visit(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a node.
            Implements preorder visiting of the node.
        """
        for c in node:
            self.visit(c)


class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self, node, verbose=0):
        self.verbose = verbose
        self.funcdefs = {}
        self.visit(node)

    def visit_FuncDef(self, node):
        if self.verbose > 0:
            print('%s at %s' % (node.decl.name, node.decl.coord))
        self.funcdefs[node.decl.name] = node


if __name__ == "__main__":
    dest_folder = 'temp_folder'
    origin_folder = r"/home/nadavsc/LIGHTBITS/code2mpi/c_parse/test/lemon"
    file_path = r"/home/nadavsc/LIGHTBITS/code2mpi/c_parse/test/basic.c"
    fake_headers_path = r"/home/nadavsc/LIGHTBITS/c_parse/pycparser/utils/fake_libc_include"
    program_dirs = [f'-I{os.path.join(root, dir)}' for (root, dirs, fnames) in os.walk(origin_folder) for dir in dirs]
    cpp_args = ["-E"] + ["-D__attribute__(x)="] + [f'-I{origin_folder}'] + program_dirs + [f"-I{fake_headers_path}"]
    pdb.set_trace()
    ast = parse_file(file_path, use_cpp=True, cpp_path='mpicc', cpp_args=cpp_args)
    func_def = FuncDefVisitor(ast)
    nodes = func_def.funcdefs

    func_call = FuncCallVisitor(nodes)
    funcs = func_call.func_calls
    print(funcs)



# mpicc -E -D'__attribute__(x)=' -Itest/lemon/check -Ipycparser/utils/fake_libc_include test/lemon/check/lemon_benchmark.c  > lemon_benchmark_pp.c