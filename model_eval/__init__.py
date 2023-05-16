import re

common_core_funcs = ['mpi _init',
                     'mp i_ finalize',
                     'mp i_ comm_ size',
                     'mp i_ comm_ rank',
                     'mp i_ recv',
                     'mp i_ send',
                     'mpi _b cast',
                     'mpi _reduce']


def metrics_calc(tp, fp, fn):
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall / (precision + recall))
    return precision, recall, f1


def prefix_function(func):
    prefix = re.search(r'mp[\s]?i[^;(]*', func)
    if prefix:
        return prefix.group().strip()
    return ''


def is_common_core(token):
    return True if token in common_core_funcs or 'reduce' in token else False


def is_mpi_func_include(tokens, mpi_funcs):
    for token in tokens:
        if token in mpi_funcs:
            return True
    return False


def get_near_tokens(token_idx, tokens):
    tokens_near = []
    for j in range(-1, 2, 1):
        if token_idx + j > 0 and token_idx + j < len(tokens):
            tokens_near.append(tokens[token_idx + j])
    return tokens_near


def conf_matrix(reference, candidate, common_core=False):
    tp = {}
    fp = {}
    fn = {}
    ref_functions = list(re.finditer(r'mp[\s]?i[\s\w_]*[(][^;]*[)][\s]?;', reference))
    cand_functions = list(re.finditer(r'mp[\s]?i[\s\w_]*[(][^;]*[)][\s]?;', candidate))
    pre_ref_functions = [prefix_function(func.group()) for func in ref_functions]
    pre_cand_functions = [prefix_function(func.group()) for func in cand_functions]
    reference = reference.split(';')
    candidate = candidate.split(';')
    reference = [prefix_function(token) for token in reference]
    candidate = [prefix_function(token) for token in candidate]
    for token_idx, token_ref in enumerate(reference):
        if token_ref in pre_ref_functions:
            if common_core and not is_common_core(token_ref):
                continue
            tokens_cand = get_near_tokens(token_idx, candidate)
            if token_ref in tokens_cand:
                tp[token_ref] = (tp[token_ref] if token_ref in tp else 0) + 1
            elif is_mpi_func_include(tokens_cand, pre_cand_functions):
                fp[token_ref] = (fp[token_ref] if token_ref in fp else 0) + 1
            else:
                fn[token_ref] = (fn[token_ref] if token_ref in fn else 0) + 1

    for token_idx, token_cand in enumerate(candidate):
        if token_cand in pre_cand_functions:
            if common_core and is_common_core(token_cand):
                continue
            tokens_ref = get_near_tokens(token_idx, reference)
            if not is_mpi_func_include(tokens_ref, pre_ref_functions):
                fp[token_cand] = (fp[token_cand] if token_cand in fp else 0) + 1
    return sum(tp.values()), sum(fp.values()), sum(fn.values())
