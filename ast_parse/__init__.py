import pdb
import re
from pycparser import c_ast, c_parser

C_GENERATOR_DICT = {'MPI_COMM_WORLD': '\(MPI_Comm\) \(\(void \*\) \(\&ompi_mpi_comm_world\)\)',
                    'MPI_COMM_SELF': '\(MPI_Comm\) \(\(void \*\) \(\&ompi_mpi_comm_self\)\)',
                    'MPI_COMM_NULL': '\(MPI_Comm\) \(\(void \*\) \(\&ompi_mpi_comm_null\)\)',
                    'MPI_INT': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_int\)\)',
                    'MPI_INTEGER': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_integer\)\)',
                    'MPI_DOUBLE': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_double\)\)',
                    'MPI_CHAR': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_char\)\)',
                    'MPI_C_BOOL': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_c_bool\)\)',
                    'MPI_BYTE': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_byte\)\)',
                    'MPI_FLOAT': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_float\)\)',
                    'MPI_LONG': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_long\)\)',
                    'MPI_UNSIGNED_LONG': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_unsigned_long\)\)',
                    'MPI_LONG_LONG_INT': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_long_long_int\)\)',
                    'MPI_2INT': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_2int\)\)',
                    'MPI_COMPLEX': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_cplex\)\)',
                    'MPI_DOUBLE_INT': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_double_int\)\)',
                    'MPI_UB': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_ub\)\)',
                    'MPI_SHORT': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_short\)\)',
                    'MPI_UNSIGNED': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_unsigned\)\)',
                    'MPI_CHARACTER': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_character\)\)',
                    'MPI_DATATYPE_NULL': '\(MPI_Datatype\) \(\(void \*\) \(\&ompi_mpi_datatype_null\)\)',
                    'MPI_BAND': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_band\)\)',
                    'MPI_MAX': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_max\)\)',
                    'MPI_MIN': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_min\)\)',
                    'MPI_SUM': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_sum\)\)',
                    'MPI_PROD': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_prod\)\)',
                    'MPI_MINLOC': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_minloc\)\)',
                    'MPI_MAXLOC': '\(MPI_Op\) \(\(void \*\) \(\&ompi_mpi_op_maxloc\)\)',
                    'MPI_ERRORS_RETURN': '\(MPI_Errhandler\) \(\(void \*\) \(\&ompi_mpi_errors_return\)\)',
                    'MPI_ERRORS_ARE_FATAL': '\(MPI_Errhandler\) \(\(void \*\) \(\&ompi_mpi_errors_are_fatal\)\)',
                    'MPI_INFO_NULL': '\(MPI_Info\) \(\(void \*\) \(\&ompi_mpi_info_null\)\)',
                    'MPI_FILE_NULL': '\(MPI_File\) \(\(void \*\) \(\&ompi_mpi_file_null\)\)',
                    'MPI_REQUEST_NULL': '\(MPI_Request\) \(\(void \*\) \(\&ompi_request_null\)\)',
                    'MPI_STATUS_IGNORE': '\(MPI_Status \*\) 0'}


def origin_funcs(mpi_re_code):
    for func, pattern in C_GENERATOR_DICT.items():
        mpi_re_code = re.sub(pattern, func, mpi_re_code)
    return mpi_re_code


def main_node(ast_file):
    for node in ast_file.ext:
        if isinstance(node, c_ast.FuncDef):
            if node.decl.name == 'main':
                return node


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
        self.array_type_dict = ['int', 'double', 'float', 'long']
        self.op_dict = {'sum': '+', 'prod': '*', 'max': '>', 'maxloc': '>', 'min': '<', 'minloc': '<'}
        self.parser = c_parser.CParser()

    def init_code(self):
        self.main = r"""
                int main(int argc,char** argv)
                {
                """
        self.code = r"""
                   int array[10];
                   int collector=0;
                   int maxvar = -99999;
                   int minvar = 99999;
                """

    def sum_loop(self, array_var, collector_var, array_type, op):
        self.code = re.sub('int', array_type, self.code)
        self.code = re.sub('array', array_var, self.code)
        self.code = re.sub('collector', collector_var, self.code)
        self.main += self.code
        self.main += fr"""
                   for (int i=0; i<sizeof({array_var}); i++) {{
                      {collector_var} {op}= {array_var}[i];
                    }}
                """
        self.main += '}'

    def maxmin_loop(self, array_var, collector_var, array_type, op):
        self.code = re.sub('int', array_type, self.code)
        self.code = re.sub('array', array_var, self.code)
        maxmin_var = 'maxvar' if op == '>' else 'minvar'
        self.code = re.sub(maxmin_var, collector_var, self.code)
        self.main += self.code
        self.main += fr"""
                   for (int i=0; i<sizeof({array_var}); i++) {{
                      if({array_var}[i] {op} {collector_var}) {{
                        {collector_var} = {array_var}[i];
                      }}
                    }}
                """
        self.main += '}'

    def reduce(self, args):
        self.init_code()
        array_var, collector_var = args[:2]
        for arg in args[2:]:
            end = arg.split('_')[-1].lower()
            if len(end) > 1 and end != 'world':
                if end in self.array_type_dict:
                    array_type = end
                    continue
                if end in self.op_dict.keys():
                    op = self.op_dict[end]
                    continue

        func = self.maxmin_loop if op == '>' or op == '<' else self.sum_loop
        func(array_var, collector_var, array_type, op)
        # print(self.main)
        ast = self.parser.parse(self.main, filename='<none>')
        return ast.ext[0].body.block_items[-1]

    def place_holder(self):
        self.init_code()
        self.main += fr"""
                   printf("___PLACEHOLDER___");
                """
        self.main += '}'
        ast = self.parser.parse(self.main, filename='<none>')
        return ast.ext[0].body.block_items[-1]


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
            # print(node)
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