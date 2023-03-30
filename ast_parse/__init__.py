import re
from pycparser import c_ast, c_parser

MPI_REMOVE_LIST = ['MPI_Init', 'MPI_Finalize', 'MPI_Comm_rank', 'MPI_Comm_free', 'MPI_Group_free',
                   'MPI_Comm_group', 'MPI_Group_incl', 'MPI_Comm_create', 'MPI_Comm_split']


class NodeTransformer(c_ast.NodeVisitor):
    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, c_ast.Node):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, c_ast.Node):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, c_ast.Node):
                new_node = self.visit(old_value)
                setattr(node, field, new_node)
        return node


def iter_fields(node):
    # this doesn't look pretty because `pycparser` decided to have structure
    # for AST node classes different from stdlib ones
    index = 0
    children = node.children()
    while index < len(children):
        name, child = children[index]
        try:
            bracket_index = name.index('[')
        except ValueError:
            yield name, child
            index += 1
        else:
            name = name[:bracket_index]
            child = getattr(node, name)
            index += len(child)
            yield name, child


class VirtualAST:
    def __init__(self):
        self.parser = c_parser.CParser()

    def init_code(self):
        self.code = r"""
                int main(int argc,char** argv)
                {
                   int array[10];
                   int collector=0;
                """

    def reduce(self, args):
        self.init_code()
        array_var, collector_var = args['UnaryOp'][0]['name'], args['UnaryOp'][1]['name']
        array_type = args['Cast'][0]['name'].split('_')[-1]
        op = args['Cast'][1]['name'].split('_')[-1]
        if op == 'sum':
            op = '+'

        self.code = re.sub('int', array_type, self.code)
        self.code = re.sub('array', array_var, self.code)
        self.code = re.sub('collector', collector_var, self.code)
        self.code += fr"""
           for (int i=1; i<sizeof({array_var}); i++) {{
              {collector_var} {op}= {array_var}[i];
            }}
        """
        self.code += '}'
        print(self.code)
        ast = self.parser.parse(self.code, filename='<none>')
        return ast.ext[0].body.block_items[2]


class MPIDetector(NodeTransformer):
    def __init__(self):
        self.is_mpi = False

    def visit_FuncCall(self, node):
        if 'MPI' in node.name.name:
            self.is_mpi = True
        return node


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