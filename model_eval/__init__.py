import re


def prefix_function(func):
    return re.search(r'mp[\s]?i[^;(]*', func).group().strip()


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
                    if abs(cand_match.span()[0]-ref_match_start) < 80:
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
    fn += abs(len(reference) - len(candidate))
    n = len(reference) if len(reference) > len(candidate) else len(candidate)
    for ref_token, cand_token in zip(reference, candidate):
        if ref_token == cand_token:
            tn += 1
        elif verbose > 0:
            print(f'ref token - {ref_token} | cand token {cand_token}')
            fn += 1
    return tn, fn, n


def metrics_calc(tp, tn, fn, fp):
    tpr = tp / (tp + fn)
    tnr = tn / (tn + fp)
    fnr = fn / (fn + tp)
    fpr = fp / (fp + tn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall / (precision + recall))
    return tpr, tnr, fnr, fpr, precision, recall, f1


def conf_matrix(reference, candidate, metrics=False):
    ref_functions = list(re.finditer(r'mp[\s]?i[^;)=]*[(][^);]*[)][\s]?;', reference))
    cand_functions = list(re.finditer(r'mp[\s]?i[^;)=]*[(][^);]*[)][\s]?;', candidate))
    ref_matches = matcher(ref_functions)
    cand_matches = matcher(cand_functions)
    tp, fp, fn, p = calc_tp_fp(ref_matches, cand_matches)
    tn, fn, n = calc_tn_fn(fn, reference, candidate, ref_matches, cand_matches)
    if metrics:
        tpr, tnr, fnr, fpr, precision, recall, f1 = metrics_calc(tp=tp, tn=tn, fn=fn, fp=fp)
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
