import re

common_core_funcs = ['mpi _init',
                     'mp i_ finalize',
                     'mp i_ comm_ size',
                     'mp i_ comm_ rank',
                     'mp i_ recv',
                     'mp i_ send',
                     'mpi _b cast',
                     'mpi _reduce']


def common_core_only(func_matches):
    core_matches = {}
    for func_name, matches in func_matches.items():
        if func_name in common_core_funcs or 'reduce' in func_name:
            core_matches[func_name] = matches
    return core_matches


def prefix_function(func):
    prefix = re.search(r'mp[\s]?i[^;(]*', func)
    if prefix:
        return prefix.group().strip()
    return ''


def remove_mpi_funcs(code, matches):
    for match in matches.keys():
        code = re.sub(rf'{match} [(](.*?)[)] ;', '', code)
    return code


def matcher(functions):
    pre_functions = [prefix_function(func.group()) for func in functions]
    funcs = {}
    for pre_func in pre_functions:
        matches = []
        if pre_func not in funcs:
            for idx, pre_func_inner in enumerate(pre_functions):
                if pre_func == pre_func_inner:
                    matches.append(functions[idx])
            funcs[pre_func] = matches
    return funcs


def is_mpi_func_include(tokens, mpi_funcs):
    for token in tokens:
        if token in mpi_funcs:
            return True
    return False


def get_near_tokens(token_idx, tokens):
    tokens_near = []
    for j in range(-2, 3, 1):
        if token_idx + j > 0 and token_idx + j < len(tokens):
            tokens_near.append(tokens[token_idx + j])
    return tokens_near


def calc_tp_fp_fn(reference, candidate, common_core=False):
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
            if common_core and token_ref not in common_core_funcs:
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
            if common_core and token_cand not in common_core_funcs:
                continue
            tokens_ref = get_near_tokens(token_idx, reference)
            if not is_mpi_func_include(tokens_ref, pre_ref_functions):
                print(token_cand)
                print(tokens_ref)
                fp[token_cand] = (fp[token_cand] if token_cand in fp else 0) + 1
    return sum(tp.values()), sum(fp.values()), sum(fn.values())


def calc_tp_fp(ref_matches, cand_matches):
    tp = {}
    fp = {}
    fn = {}
    p = 0
    for func, ref_match in ref_matches.items():
        matches = 0
        ref_match_starts = [match.span()[0] for match in ref_match]
        for ref_match_start in ref_match_starts:
            p += 1
            if func in cand_matches:
                for cand_match in cand_matches[func]:
                    if abs(cand_match.span()[0]-ref_match_start) < 100:
                        matches += 1
                        tp[func] = (tp[func] if func in tp else 0) + 1
            else:
                fn[func] = (fn[func] if func in fn else 0) + 1
        if func in cand_matches:
            if len(ref_match_starts) < len(cand_matches[func]):
                fp[func] = (fp[func] if func in fp else 0) + len(cand_matches[func]) - matches
            elif len(ref_match_starts) != len(cand_matches[func]):
                fn[func] = (fn[func] if func in fn else 0) + len(ref_match_starts) - matches

    for func, cand_match in cand_matches.items():
        for match in cand_match:
            if func not in ref_matches:
                fp[func] = (fp[func] if func in fp else 0) + 1
    return sum(tp.values()), sum(fp.values()), sum(fn.values()), p


def calc_tn_fn(fn, reference, candidate, ref_matches, cand_matches, verbose=0):
    reference = remove_mpi_funcs(reference, ref_matches)
    candidate = remove_mpi_funcs(candidate, cand_matches)
    reference = reference.split()
    candidate = candidate.split()
    tn = 0
    # fn += abs(len(reference) - len(candidate))
    n = len(reference) if len(reference) > len(candidate) else len(candidate)
    for ref_token, cand_token in zip(reference, candidate):
        if ref_token == cand_token:
            tn += 1
        elif verbose > 0:
            print(f'ref token - {ref_token} | cand token {cand_token}')
            # fn += 1
    return tn, fn, n


def metrics_calc(tp, tn, fn, fp):
    # tpr = tp / (tp + fn)
    # tnr = tn / (tn + fp)
    # fnr = fn / (fn + tp)
    # fpr = fp / (fp + tn)
    tpr = 0
    tnr = 0
    fnr = 0
    fpr = 0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall / (precision + recall))
    return tpr, tnr, fnr, fpr, precision, recall, f1


def conf_matrix(reference, candidate, metrics=False, common_core=False):
    tp, fp, fn = calc_tp_fp_fn(reference, candidate, common_core)
    # ref_functions = list(re.finditer(r'mp[\s]?i[\s\w_]*[(][^;]*[)][\s]?;', reference))
    # cand_functions = list(re.finditer(r'mp[\s]?i[\s\w_]*[(][^;]*[)][\s]?;', candidate))
    # ref_matches = common_core_only(matcher(ref_functions)) if common_core else matcher(ref_functions)
    # cand_matches = common_core_only(matcher(cand_functions)) if common_core else matcher(cand_functions)
    #
    # tp, fp, fn, p = calc_tp_fp(ref_matches, cand_matches)
    # tn, fn, n = calc_tn_fn(fn, reference, candidate, ref_matches, cand_matches)
    # if metrics:
    #     tpr, tnr, fnr, fpr, precision, recall, f1 = metrics_calc(tp=tp, tn=tn, fn=fn, fp=fp)
    tn = 0
    p = 0
    n = 0
    return tp, fp, tn, fn, p, n


if __name__ == "__main__":
    results_path = '/home/nadavsc/LIGHTBITS/SPT-Code/outputs/3_epochs_320/translation_test_results.txt'
    with open(results_path, 'r') as f:
        results = f.read()
    references = re.findall(r'reference: (.*?)\n', results)
    candidates = re.findall(r'candidate: (.*?)\n', results)
    all_tp, all_fp, all_tn, all_fn, all_p, all_n = (0, 0, 0, 0, 0, 0)
    for idx, (reference, candidate) in enumerate(zip(references, candidates)):
        tp, fp, tn, fn, p, n = conf_matrix(reference, candidate, metrics=False)
        all_tp += tp
        all_fp += fp
        all_tn += tn
        all_fn += fn
        all_p += p
        all_n += n
        print(idx)
    tpr, tnr, fnr, fpr, precision, recall, f1 = metrics_calc(tp=all_tp, tn=all_tn, fn=all_fn, fp=all_fp)
    # print(f'TP: {tp} TN: {tn} FP: {fp} FN: {fn}')
    print(f'TPR: {tpr:.2f} | TNR: {tnr:.2f} | FNR: {fnr:.2f} | FPR: {fpr:.2f}')
    print(f'Precision: {precision:.2f}')
    print(f'Recall: {recall:.2f}')
    print(f'F1: {f1:.2f}')
