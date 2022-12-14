from files_parser import load_file, files_walk, count_lines, mpi_in_line, openmp_in_line, is_include
from file_slice import find_init_final, comment_in_ranges

from logger import set_logger, info


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


def init_finalize_count(db):
    count = 0
    for id, repo in db.items():
        for program_id, program_path in repo['programs'].items():
            for fpath in files_walk(program_path):
                lines, name, ext = load_file(fpath, load_by_line=False)
                if ext == '.c':
                    lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments=True)
                    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
                        count += 1
                        num_lines = len(count_lines(lines))
                        init_finalize_lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
                        num_lines_init_finalize = len(count_lines(init_finalize_lines)) + 1
                        ratio = num_lines_init_finalize/num_lines
                        info(f'{count} Init-Finalize programs\nAll lines: {num_lines}, Init-Finalize: {num_lines_init_finalize}, Ratio: {ratio:.2f}\n')
    return count
