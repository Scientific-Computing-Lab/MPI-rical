import pickle
import json
import os
import sys
from tqdm import tqdm

sys.path.extend(['.', '..' ,'../parsers'])
from pycparser import c_ast, c_generator
from ast_parse import CounterIdVisitor
from replace_vars import ReplaceIdsVisitor


def load_sample(sample_path):
    with open(os.path.join(sample_path, 'ast.pickle'), 'rb') as f:
        pass
        asts = pickle.load(f)

    with open(os.path.join(sample_path, f'code.c'), 'r') as f:
        code = f.read()
    return asts.ast_loop, code


db_path = '/home/talkad/Downloads/thesis/data_gathering_script/samples/sample_c.json'
save_dir = '/home/talkad/LIGHTBITS_SHARE/c_replaced/'

with open(db_path, 'r') as df_file:
    sample_path = json.load(df_file)

# fix samples path
sample_path = {int(idx):('/home/talkad/'+path[9:]) for idx, path in sample_path.items()}


find_variables = CounterIdVisitor()
generator = c_generator.CGenerator()

for path in tqdm(sample_path.values()): #[sample_path[0], sample_path[1], sample_path[2], sample_path[3]]:
    sample_new_path = os.path.join(save_dir, path[37:])
    os.makedirs(sample_new_path)

    omp_pragma, ast_loop, code = load_sample(path)
    find_variables.visit(ast_loop)

    replacor = ReplaceIdsVisitor(find_variables.ids, find_variables.array, find_variables.struct, find_variables.func)
    replacor.visit(ast_loop)

    # create sample
    with open(os.path.join(sample_new_path, 'ast.pickle'), 'wb') as f:
        pickle.dump(ast_loop, f)

    with open(os.path.join(sample_new_path, f'code.c'), 'w') as f:
        f.write(generator.visit(ast_loop))

    if omp_pragma is not None:
        with open(os.path.join(sample_new_path, 'pragma.pickle'), 'wb') as f:
            pickle.dump(omp_pragma, f)

    find_variables.reset()


# print(sample_path[1])
# omp_pragma, ast_loop, code = load_sample(sample_path[1])

# print(code)
# # print(ast_loop)

# find_variables = CounterIdVisitor()
# find_variables.visit(ast_loop)

# generator = c_generator.CGenerator()

# # Replace the names
# replacor = ReplaceIdsVisitor(find_variables.ids, find_variables.array, find_variables.struct, find_variables.func)
# replacor.visit(ast_loop)

# print(generator.visit(ast_loop))

# # replacor.visit(ast_loop)
# # print(replacor.var_prefix)