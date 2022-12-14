import os
import re

from files_parser import load_file, name_split
from repos_parser import make_dst_folder, FORTRAN_EXTENSIONS


def line_endings_correction(lines):
    lines = re.sub(r"\\n", "\n", lines)
    lines = re.sub(r"\\t", "\t", lines)
    lines = re.sub(r"\\r", "\r", lines)  # \\r is new line in MAC
    return lines


def comment_matches(lines, ext):
    if ext in FORTRAN_EXTENSIONS:
        return [match for match in re.finditer(r'C[\s].*', lines, flags=re.IGNORECASE)]
    return [match for match in re.finditer(r'\/\*(.*?)\*\/', lines, flags=re.IGNORECASE)]  # r'\/\*[^!]*?\*\/'


def comment_ranges(lines, ext):
    return [range(match.span()[0], match.span()[1]) for match in comment_matches(lines, ext)]


def comment_in_ranges(match, lines, ext):
    for print_range in comment_ranges(lines, ext):
        if match.span()[0] in print_range:
            return True
    return False


def del_comment_line(lines, ext):
    pattern = r'[!][\s]*.*?[\\]*[\\][n]' if ext in FORTRAN_EXTENSIONS else r'[\/][\/].*?[\\]*[\\][n]'
    return re.sub(pattern, '', lines, flags=re.IGNORECASE)


def del_comments(lines, ext):
    lines = del_comment_line(lines, ext)
    if ext not in FORTRAN_EXTENSIONS:
        return re.sub(r'\/\*(.*?)\*\/', '', lines, flags=re.IGNORECASE)


def write_to_file(dst, lines, name, ext):
    make_dst_folder(dst)
    with open(os.path.join(os.path.split(dst)[0], f'{name}_sliced{ext}'), "w") as f:
        f.write(lines)


def find_init_final(lines, ext, rm_comments=True):
    if rm_comments:
        lines = del_comments(lines, ext)
    init_match = re.search(r'[n]\s*[a-z^n]*\s*MPI_Init.*?[\\]*[\\][n]', lines, flags=re.IGNORECASE)
    finalize_matches = [match for match in re.finditer(r'MPI_Finalize[^\\]*', lines, flags=re.IGNORECASE)]
    return lines, init_match, finalize_matches


def init_final_slice(path, dst, rm_comments=True):
    lines, name, ext = load_file(path, load_by_line=False)
    lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments)
    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
        lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
        lines = line_endings_correction(lines)
        write_to_file(dst, lines, name, ext)
        return True
    return False