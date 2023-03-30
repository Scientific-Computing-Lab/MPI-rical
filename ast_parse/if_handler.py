import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'ast_parse'))
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parse'))
sys.path.append(os.path.join(project_path, 'queries'))

from ast_parse import MPIDetector, NodeTransformer
from ast import ast, re_code
from files_handler import load_pkl


class IfCallsHandler(NodeTransformer):
    def if_ext(self, node):
        try:
            iftrue = node.iftrue
            self.if_content += iftrue.block_items
        except:
            self.if_content += node.block_items
            return

        iffalse = node.iffalse
        if iffalse is not None:
            self.if_ext(iffalse)

    def visit_If(self, node):
        var_name = node.cond.left.name
        mpi_detector = MPIDetector()
        mpi_detector.visit(node)

        if 'rank' in var_name or mpi_detector.is_mpi:
            self.if_content = []
            self.if_ext(node)
            return self.if_content
        return node


ast_file = load_pkl(path='test_if/ast.pkl')
# ast_file = ast(origin_folder='test_if', fake_headers_path='test_if', save_dir='test_if')
v = IfCallsHandler()
v.visit(ast_file)
re_code(ast_file, 'test_if')
