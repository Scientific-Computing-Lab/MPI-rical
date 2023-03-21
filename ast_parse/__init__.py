from pycparser import c_ast


# Puts in array all the ids found, function name(calls), array and structs
class CounterIdVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.reset()

    def visit_ID(self, node):
        if node.name:
            self.ids.append(node.name)

    def visit_FuncCall(self, node):
        try:
            if isinstance(node.name, c_ast.UnaryOp):
                if node.name.op == '*':
                    self.generic_visit(node)
            else:
                self.func.append(node.name.name)
                self.generic_visit(node)
        except:
            pass

    def visit_ArrayRef(self, node):
        if isinstance(node.name, c_ast.BinaryOp):
            self.generic_visit(node)
            return
        # CASTING
        if isinstance(node.name, c_ast.Cast):
            if isinstance(node.name.expr, c_ast.ID) or isinstance(node.name.expr, c_ast.ArrayRef):
                name = node.name.expr.name
            if isinstance(node.name.expr, c_ast.StructRef):
                name = node.name.expr.field
            if isinstance(node.name.expr, c_ast.UnaryOp):
                if isinstance(node.name.expr.expr, c_ast.ArrayRef):
                    self.generic_visit(node)
                    return
                name = node.name.expr.expr.name
        # ARRAY OF STRUCT
        if isinstance(node.name, c_ast.StructRef):
            name = node.name.field
        # NORMAL
        if isinstance(node.name, c_ast.ID):
            name = node.name.name
        # UNARY OP WHICH IS BASICALLY CAST TO STRUCT..
        if isinstance(node.name, c_ast.UnaryOp):
            if isinstance(node.name.expr, c_ast.StructRef):
                name = node.name.expr.field
            if isinstance(node.name.expr, c_ast.ID):
                name = node.name.expr.name
        if isinstance(node.name, c_ast.ArrayRef):
            # if it is an array of arrays (2d array etc, we will just continue to the next expr..)
            self.generic_visit(node)
            return
        try:
            if isinstance(name, c_ast.ID):
                name = name.name
            self.array.append(name)
            self.generic_visit(node)
        except:
            pass
            # print(node.name)
            # exit(1)

    def visit_ArrayDecl(self, node):
        if isinstance(node.type, c_ast.PtrDecl):
            name = node.type.type.declname
        if isinstance(node.type, c_ast.TypeDecl):
            name = node.type.declname
        if isinstance(node.type, c_ast.ArrayDecl):
            self.generic_visit(node)
            return
        try:
            self.array.append(name)
            self.generic_visit(node)
        except:
            print(node)
            exit(1)

    def visit_StructRef(self, node):
        if isinstance(node.name, c_ast.ID):
            name = node.name.name
            self.struct.append(name)
        self.generic_visit(node)

    def reset(self):
        self.ids = []
        self.func = []
        self.array = []
        self.struct = []