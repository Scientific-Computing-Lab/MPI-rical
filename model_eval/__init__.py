import re

from files_handler import load_pkl, load_file

scoring_funcs = ['mpi _init',
                 'mp i_ finalize',
                 'mp i_ comm_ size',
                 'mp i_ comm_ rank',
                 'mp i_ recv',
                 'mp i_ send'
                 'mp i_ abort',
                 'mpi _bar rier',
                 'mpi _type_ commit',
                 'mpi _b cast',
                 'mp i_ comm_ free',
                 'mp i_ w time',
                 'mpi _reduce',
                 'mp i_ win _create',
                 'mp i_ all reduce',
                 'mp i_ wait',
                 'mp i_ i recv',
                 'mp i_ isend']


def remove_mpi_funcs(code, matches):
    for match in matches.keys():
        code = re.sub(rf'{match} [(](.*?)[)] ;', '', code)
    return code


def matcher(code):
    funcs = {}
    count = {}
    for pattern in scoring_funcs:
        ref_matches = list(re.finditer(pattern, code))
        if ref_matches:
            count[pattern] = (count[pattern] if pattern in count else 0) + len(ref_matches)
            funcs[pattern] = ref_matches
    return funcs, count


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
                    if abs(cand_match.span()[0]-ref_match_start) < 120:
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
    ref_matches, ref_counts = matcher(reference)
    cand_matches, cand_counts = matcher(candidate)
    tp, fp, fn, p = calc_tp_fp(ref_matches, cand_matches)
    tn, fn, n = calc_tn_fn(fn, reference, candidate, ref_matches, cand_matches)
    if metrics:
        tpr, tnr, fnr, fpr, precision, recall, f1 = metrics_calc(tp=tp, tn=tn, fn=fn, fp=fp)
    return tp, fp, tn, fn, p, n


# # reference = 'int main ( int argc , char * * argv ) { int nprocs ; int rank ; mpi _init ( & argc , & argv ) ; mp i_ comm_ size ( mp i_ comm_ world , & nprocs ) ; mp i_ comm_ rank ( mp i_ comm_ world , & rank ) ; printf ( ___str , nprocs , rank ) ; int * array = malloc ( 1000 * ( sizeof ( int ) ) ) ; int i ; int j ; int j max = 50 ; for ( j = 0 ; j < j max ; j ++ ) { int tag = j + 1 ; for ( i = 0 ; i < 1000 ; i ++ ) { array [ i ] = ( rank * i ) + j ; } if ( ( rank == 0 ) & & ( nprocs > 1 ) ) { for ( i = 1 ; i < nprocs ; i ++ ) { mpi _request req ; mp i_ i recv ( array , 1000 , mp i_ int , i , tag , mp i_ comm_ world , & req ) ; float junk = do work ( ) ; if ( junk == 0 . 00 ) printf ( ___str ) ; mp i_ wait ( & req , mp i_ status_ ignore ) ; } } else { mpi _request req ; mp i_ isend ( array , 1000 , mp i_'
# # candidate = 'int main ( int argc , char * * argv ) { int nprocs ; int rank ; mpi _init ( & argc , & argv ) ; mp i_ comm_ size ( mp i_ comm_ world , & nprocs ) ; mp i_ comm_ rank ( mp i_ comm_ world , & rank ) ; printf ( ___str , nprocs , rank ) ; int * array = malloc ( 1000 * ( sizeof ( int ) ) ) ; int i ; int j ; int j max = 50 ; for ( j = 0 ; j < j max ; j ++ ) { int tag = j + 1 ; for ( i = 0 ; i < 1000 ; i ++ ) { array [ i ] = ( rank * i ) + j ; } if ( ( rank == 0 ) & & ( nprocs > 1 ) ) { for ( i = 1 ; i < nprocs ; i ++ ) { mpi _request req ; mp i_ i recv ( array , 1000 , mp i_ int , i , tag , mp i_ comm_ world , & req ) ; mp i_ wait ( & req , mp i_ status_ ignore ) ; float junk = do work ( ) ; if ( junk == 0 . 00 ) printf ( ___str ) ; } } else { mpi _request req ; mp i_ i recv ( array , 1000 ,'
# reference = 'int main ( int argc , char * * argv ) { mpi _init ( & argc , & argv ) ; int rank ; int com size ; mp i_ comm_ size ( mp i_ comm_ world , & com size ) ; mp i_ comm_ rank ( mp i_ comm_ world , & rank ) ; long long int local arraysize = ( ( ( long long int ) 1 ) < < 30 ) / com size ; long long int * local array = ( long long int * ) malloc ( local arraysize * ( sizeof ( long long int ) ) ) ; for ( long long int i = 0 ; i < local arraysize ; i ++ ) local array [ i ] = ( ( ( long long int ) rank ) * local arraysize ) + i ; long long int result ; uint64 _t starttime = clock _now ( ) ; mpi _p2 p_ reduce ( local array , & result , local arraysize , ( mp i_ datatype ) ( ( void * ) ( & o mp i_ mp i_ long_ long _int ) ) , mpi _sum , 0 , mp i_ comm_ world ) ; uint64 _t endtime = clock _now ( ) ; double time _in_ secs = ( ( double ) ( endtime - starttime ) ) / 512 000000 ; if ( rank == 0 ) printf ( ___str , result , time _in_ secs ) ; starttime = clock _now ( ) ; long long int local sum = 0 ; for ( long long int i = 0 ; i < local arraysize ; i ++ ) local sum += local array [ i ] ; mpi _reduce ( & local sum , & result , 1 , ( mp i_ datatype ) ( ( void * ) ('
# candidate = 'int main ( int argc , char * * argv ) { int rank ; int com size ; mpi _init ( & argc , & argv ) ; mp i_ comm_ rank ( mp i_ comm_ world , & rank ) ; mp i_ comm_ size ( mp i_ comm_ world , & com size ) ; mp i_ comm_ size ( mp i_ comm_ world , & com size ) ; long long int local arraysize = ( ( ( long long int ) 1 ) < < 30 ) / com size ; long long int * local array = ( long long int * ) malloc ( local arraysize * ( sizeof ( long long int ) ) ) ; for ( long long int i = 0 ; i < local arraysize ; i ++ ) local array [ i ] = ( ( ( long long int ) rank ) * local arraysize ) + i ; long long int result ; uint64 _t starttime = clock _now ( ) ; uint64 _t endtime = clock _now ( ) ; double time _in_ secs = ( ( double ) ( endtime - starttime ) ) / 512 000000 ; if ( rank == 0 ) printf ( ___str , result , time _in_ secs ) ; starttime = clock _now ( ) ; long long int local sum = 0 ; for ( long long int i = 0 ; i < local arraysize ; i ++ ) local sum += local array [ i ] ; endtime = clock _now ( ) ; time _in_ secs = ( ( double ) ( endtime - starttime ) ) / 512 000000 ; if ( rank == 0 ) printf ( ___str , result , time _in_ secs ) ; free ( local array ) ; mp i_ finalize ( ) ; return 0 ; }'
# print(f'Reference: {reference}')
# print(f'Candidate: {candidate}')
# conf_matrix(reference, candidate)


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
