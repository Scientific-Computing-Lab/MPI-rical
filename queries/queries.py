from files_parse import remove_comments, count_lines, mpi_in_line, openmp_in_line, is_include, find_init_final, comment_in_ranges
from files_handler import load_file, files_walk, write_to_json
from funcs_extract_reg import functions_in_header


from logger import info


def openmp_mpi_count(db):
    count = 0
    for id, repo in db.items():
        for program_id, program_path in repo['programs'].items():
            mpi_include = False
            openmp_include = False
            fpaths = files_walk(program_path)
            for fpath in fpaths:
                if is_include(fpath, mpi_in_line):
                    mpi_include = True
                if is_include(fpath, openmp_in_line):
                    openmp_include = True
                if mpi_include and openmp_include:
                    info(f'{count} programs have been found')
                    count += 1
                    break
    return count


def init_finalize_count(programs_db):
    count = 0
    for repo in programs_db.values():
        for program_path in repo['programs'].values():
            for fpath in files_walk(program_path):
                lines, name, ext = load_file(fpath, load_by_line=False)
                if ext == '.c':
                    lines, init_match, finalize_matches = find_init_final(lines, rm_comments=True)
                    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):  ##TODO: write a comment in ranges function
                        count += 1
                        num_lines = len(count_lines(lines))
                        init_finalize_lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
                        num_lines_init_finalize = len(count_lines(init_finalize_lines)) + 1
                        ratio = num_lines_init_finalize/num_lines
                        info(f'{count} Init-Finalize programs\nAll lines: {num_lines}, Init-Finalize: {num_lines_init_finalize}, Ratio: {ratio:.2f}\n')
    return count


def functions_finder(origin_db):
    database = {}
    repo_idx = 0
    for user_id in origin_db.keys():
        for repo in origin_db[user_id]['repos'].values():
            database[repo_idx] = {'name': repo['name'], 'path': repo['path'], 'headers': {}}
            for fpath in files_walk(repo['path']):
                lines, name, ext = load_file(fpath, load_by_line=False)
                lines = remove_comments(lines)  # remove for c only
                if ext == '.h' and name not in database[repo_idx]['headers'].keys():
                    header_functions = [f_header for f_header in functions_in_header(lines)]
                    database[repo_idx]['headers'][name] = header_functions
                    print(header_functions)
            repo_idx += 1
    write_to_json(database, 'header_funcs.json')