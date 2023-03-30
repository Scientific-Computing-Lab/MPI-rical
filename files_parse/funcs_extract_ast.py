from pycparser import c_ast


class FuncCallVisitor(c_ast.NodeVisitor):
    """
    Travels the node and define whether it contains func call in it
    """
    def __init__(self, nodes, verbose=0):
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


def func_export(ast):
    func_def = FuncDefVisitor(ast)
    nodes = func_def.funcdefs
    func_call = FuncCallVisitor(nodes)
    funcs = func_call.func_calls
    return funcs