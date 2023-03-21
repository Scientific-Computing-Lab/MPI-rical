import json
import re
import random
from pycparser import c_ast
from pycparser.plyparser import Coord
from collections import OrderedDict


VAR_PREFIX = "var"
ARR_PREFIX = "arr"
FUNC_PREFIX = "func"
STRUCT_PREFIX = "struct"


# Puts in array all the ids found, function name(calls), array and structs
class ReplaceIdsVisitor(c_ast.NodeVisitor):
    def __init__(self, var, array, struct, func):
        # remove duplicates..
        self.var = list(OrderedDict.fromkeys(var))
        self.array = list(OrderedDict.fromkeys(array))
        self.struct = list(OrderedDict.fromkeys(struct))
        self.func = list(OrderedDict.fromkeys(func))

        # now remove from self.var all the names from array struct and func
        self.var = [v for v in self.var if v not in self.array]
        self.var = [v for v in self.var if v not in self.struct]
        self.var = [v for v in self.var if v not in self.func]

        self.name_mapping = {}
        for type, names in zip([VAR_PREFIX, ARR_PREFIX, FUNC_PREFIX, STRUCT_PREFIX],
                                [self.var, self.array, self.func, self.struct]):
            idxs = list(range(len(names)))
            random.shuffle(idxs)
            # print(idxs)
            # print(names)

            for idx, name in zip(idxs, names):
                self.name_mapping[name] = f'{type}_{idx}'

    def visit_ID(self, node):
        if node.name in self.name_mapping:
            node.name = self.name_mapping[node.name]

    def visit_Decl(self, node):
        if node.name in self.name_mapping:
            node.name = self.name_mapping[node.name]

    def visit_TypeDecl(self, node):
        if node.declname in self.name_mapping:
            node.declname = self.name_mapping[node.declname]

    def visit_ArrayDecl(self, node):
        if isinstance(node.type, c_ast.PtrDecl):
            if node.type.type.declname in self.name_mapping:
                node.type.type.declname = self.name_mapping[node.type.type.declname]
        if isinstance(node.type, c_ast.TypeDecl):
            if node.type.declname in self.name_mapping:
                node.type.declname= self.name_mapping[node.type.declname]

    def reset(self):
        self.var = []
        self.array = []
        self.struct = []
        self.func = []


