import pdb
import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'ast_parse'))
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parse'))
sys.path.append(os.path.join(project_path, 'queries'))

from ast_parse import NodeTransformer
from c_ast import ast, re_code
from files_handler import load_pkl


class MPIDetector(NodeTransformer):
    def __init__(self):
        self.is_mpi = False

    def visit_FuncCall(self, node):
        if 'MPI' in node.name.name:
            self.is_mpi = True
        return node


class RankDetector(NodeTransformer):
    def __init__(self):
        self.is_rank = False

    def visit_ID(self, node):
        if 'rank' in node.name:
            self.is_rank = True
        return node


class IfCallsHandler(NodeTransformer):
    def if_ext(self, node):
        # print('START')
        # pdb.set_trace()
        try:
            iftrue = node.iftrue
            try:
                self.if_content += iftrue.block_items
            except:
                # print('First Exception')
                # pdb.set_trace()
                try:
                    self.if_content += node.block_items
                except:
                    # print('Second Exception')
                    # pdb.set_trace()
                    self.if_content += [iftrue]
        except:
            pass
        try:
            iffalse = node.iffalse
            if iffalse is not None:
                self.if_ext(iffalse)
        except:
            # print('END')
            # pdb.set_trace()
            self.if_content += [node]
        return

    def visit_If(self, node):
        mpi_detector = MPIDetector()
        rank_detector = RankDetector()

        mpi_detector.visit(node)
        rank_detector.visit(node.cond)

        if rank_detector.is_rank or mpi_detector.is_mpi:
            self.if_content = []
            self.if_ext(node)
            # pdb.set_trace()
            return self.if_content
        return node


# ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI/Terminus-IMRC_mpi-ping-pong-bench_0/ast.pkl')
# # ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI/brlindblom_gepetools_0/ast.pkl')
# # ast_file = load_pkl(path='/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI/c0mpsc1_MPIProgLib_0/ast.pkl')
# # ast_file = ast(origin_folder='test_if', fake_headers_path='test_if', save_dir='test_if')
# v = IfCallsHandler()
# v.visit(ast_file.ext[-1])
# pdb.set_trace()
# re_code(ast_file, 'test')
