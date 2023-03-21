import os
import re

from files_parser import space_remove

'''
A collection of functions for functions extraction with Regex. 
'''


def function_starter(function):
    return [space_remove(match.group()) for match in re.finditer(r'[a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[({]', function, flags=re.IGNORECASE)]


def match_funcs(pre_funcs, funcs):
    for pre_func in pre_funcs:
        for func in funcs:
            start_pre_func = function_starter(pre_func)
            start_func = function_starter(func)
            if start_pre_func and start_func:
                if start_pre_func[0] == start_func[0]:
                    return True
    return False


def database_functions_parser(functions_db, repo_path, headers_path):
    couples = []
    files = functions_db[repo_path]['files']
    if not files:
        return couples
    headers_path = [h_path for h_path in headers_path if h_path in list(files.keys())]
    for h_path in headers_path:
        for f_path, functions in files.items():
            if os.path.splitext(f_path)[-1] == '.c':
                if match_funcs(files[h_path]['functions'], functions['functions']):
                    couples.append(f_path)
    return list(set(couples))


def functions_implementations(lines):
    return re.findall(r'[a-z]*\s[a-z*]*[(](.*?)[)]\s{', lines, flags=re.IGNORECASE)


def functions_in_header(lines):
    return [space_remove(match.group()) for match in re.finditer(r'[\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[(]', lines, flags=re.IGNORECASE)]
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s[a-z0-9_*\\]*\s*[(]
# [\\][n][a-z0-9_*]+\s[a-z0-9_*]+\s[a-z0-9_*]*\s*[(]
# [\\][n][a-z0-9*]*\s[a-z0-9_*]*[(](.*?)[)];
# \\n\s*(?:[\w\*]+\s+)?\w+\s*\([^;]*\)\s*(?:const)?\s*(?:[^;]*;)


def prefix_include(lines):
    return list(re.finditer(r'^if[\s(]', lines, flags=re.IGNORECASE)) + \
           list(re.finditer(r'^else[\s(]', lines, flags=re.IGNORECASE)) + \
           list(re.finditer(r'^case[\s]', lines, flags=re.IGNORECASE))


def functions_in_c(lines):
    return [space_remove(match.group()) for match in re.finditer(r'[\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[^{(;]*\([^)]*\)[^{;]*{', lines, flags=re.IGNORECASE)]
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[^(;]*\([^)]*\)[^{;]*{
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[^(]*\([^)]*\)[^{;]*{
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[(](.*?)[)]([\\][n])*\s*[{]
# [\\][n][a-z0-9_*\\]+\s[a-z0-9_*\\]+\s*[a-z0-9_*\\]*\s*[{]


def functions_in_file(lines, ext):
    functions = functions_in_c(lines)
    if ext == '.h':
        functions += functions_in_header(lines)
    return [func for func in functions if len(func) < 350 and not prefix_include(func)]
