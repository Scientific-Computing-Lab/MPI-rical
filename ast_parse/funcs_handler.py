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
from ast import re_code
from files_handler import load_pkl


class FuncCallsHandler(NodeTransformer):
    def __init__(self):
        self.vast = VirtualAST()

    def get_args(self, node):
        args = {'UnaryOp': {}, 'Constant': {}, 'Cast': {}}
        for arg in list(node.args.exprs):
            if isinstance(arg, c_ast.UnaryOp):
                args['UnaryOp'][len(args['UnaryOp'])] = {'op': arg.op, 'name': arg.expr.name}
            if isinstance(arg, c_ast.Constant):
                args['Constant'][len(args['Constant'])] = {'type': arg.type, 'value': arg.value}
            if isinstance(arg, c_ast.Cast):
                args['Cast'][len(args['Cast'])] = {'name': arg.expr.expr.expr.name}
        return args

    def visit_FuncCall(self, node):
        name = node.name.name
        if name in MPI_REMOVE_LIST:
            print(node.name.name)
            return None

        if name == 'MPI_Reduce' or name == 'MPI_Allreduce':
            args = self.get_args(node)
            node = self.vast.reduce(args)
        return node


ast_file = load_pkl(path='test/ast.pkl')
v = FuncCallsHandler()
v.visit(ast_file)
re_code(ast_file, 'test')
