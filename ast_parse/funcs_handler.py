import pdb
import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'ast_parse'))
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parse'))
sys.path.append(os.path.join(project_path, 'queries'))

from pycparser import c_ast
from ast_parse import VirtualAST, NodeTransformer, MPI_REMOVE_LIST
from c_ast import re_code
from files_handler import load_pkl


class FuncCallsHandler(NodeTransformer):
    def __init__(self):
        self.virtual_ast = VirtualAST()

    def get_args(self, node):
        args = []
        for idx, arg in enumerate(list(node.args.exprs)):
            if isinstance(arg, c_ast.ID):
                args.append(arg.name)
            if isinstance(arg, c_ast.ArrayRef):
                args.append(arg.subscript.value)
            if isinstance(arg, c_ast.StructRef):
                args.append(arg.name.name + arg.type + arg.field.name)
            if isinstance(arg, c_ast.UnaryOp):
                args.append(arg.expr.name)
            if isinstance(arg, c_ast.Constant):
                args.append(arg.value)
            if isinstance(arg, c_ast.Cast):
                args.append(arg.expr.expr.expr.name)
        return args

    def visit_FuncCall(self, node):
        name = node.name.name
        if name == 'MPI_Reduce' or name == 'MPI_Allreduce':
            try:
                args = self.get_args(node)
                node = self.virtual_ast.reduce(args)
            except:
                print(f'{name} has failed')
                return None
        elif 'MPI' in name:
            return None
        return node


class FuncCallsPlaceHolder(NodeTransformer):
    def __init__(self):
        self.virtual_ast = VirtualAST()

    def visit_FuncCall(self, node):
        name = node.name.name
        if 'MPI' in name:
            return self.virtual_ast.place_holder()
        return node


# ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI/Terminus-IMRC_mpi-ping-pong-bench_0/ast.pkl')
# # ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/ast_parse/test/ast.pkl')
# # ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI/brlindblom_gepetools_0/ast.pkl')
# # ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI/c0mpsc1_MPIProgLib_0/ast.pkl')
# pdb.set_trace()
# v = FuncCallsHandler()
# v.visit(ast_file.ext[-1])
# re_code(ast_file, 'test')
