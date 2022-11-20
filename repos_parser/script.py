import os
import re

from logger import set_logger, info
from repos_parser import make_dst_folder, get_extension, FORTRAN_EXTENSIONS


class Script:
    def __init__(self, fname, path, load_by_line=True):
        self.fname = fname
        self.path = path
        self.name = self.fname.split('.')[0]
        self.ext = get_extension(fname)
        self.load_by_line = load_by_line
        self.lines = self.load_script()

        self.funcs_counter = {}
        self.mpi_funcs_counter()

    def load_script(self):
        with open(self.path, 'rb') as f:
            if self.load_by_line:
                return f.readlines()
            return str(f.read())

    def is_mpi_included(self, line):
        line = str(line).lower()
        if self.ext in FORTRAN_EXTENSIONS:
            return 'include' in line and 'mpif.h' in line
        return '#include' in line and 'mpi.h' in line

    def is_print_included(self, line):
        if self.ext in FORTRAN_EXTENSIONS:
            return 'print' in line
        else:
            return ('printf' in line) or ('cout' in line)

    def mpi_funcs_counter(self):
        funcs = []
        for line in self.lines:
            line = str(line)
            if not self.is_print_included(line):
                funcs += re.findall('MPI_\w*', line)  # \S* for all the function
        for func in funcs:
            self.funcs_counter[func] = (self.funcs_counter[func] if func in self.funcs_counter else 0) + 1

    def line_endings_correction(self):
        self.lines = re.sub(r"\\n", "\n", self.lines)
        self.lines = re.sub(r"\\t", "\t", self.lines)
        self.lines = re.sub(r"\\r", "\r", self.lines)  # \\r is new line in MAC

    def comment_matches(self):
        if self.ext in FORTRAN_EXTENSIONS:
            return [match for match in re.finditer(r'C[\s].*', self.lines, flags=re.IGNORECASE)]
        return [match for match in re.finditer(r'\/\*(.*?)\*\/', self.lines, flags=re.IGNORECASE)]  # r'\/\*[^!]*?\*\/'

    def comment_ranges(self):
        comment_matches = self.comment_matches()
        return [range(match.span()[0], match.span()[1]) for match in comment_matches]

    def in_comment_ranges(self, match):
        comment_ranges = self.comment_ranges()
        for print_range in comment_ranges:
            if match.span()[0] in print_range:
                return True
        return False

    def del_comment_line(self):
        pattern = r'[!][\s]*.*?[\\]*[\\][n]' if self.ext in FORTRAN_EXTENSIONS else r'[\/][\/].*?[\\]*[\\][n]'
        self.lines = re.sub(pattern, '', self.lines, flags=re.IGNORECASE)

    def del_comments(self):
        self.del_comment_line()
        if self.ext not in FORTRAN_EXTENSIONS:
            self.lines = re.sub(r'\/\*(.*?)\*\/', '', self.lines, flags=re.IGNORECASE)

    def init_final_slice(self, dir, comments=False):
        if not comments:
            self.del_comments()
        init_match = re.search(r'[n]\s*[a-z^n]*\s*MPI_Init.*?[\\]*[\\][n]', self.lines, flags=re.IGNORECASE)
        finalize_matches = [match for match in re.finditer(r'MPI_Finalize[^\\]*', self.lines, flags=re.IGNORECASE)]
        if init_match and finalize_matches and not self.in_comment_ranges(init_match):
            self.lines = self.lines[init_match.span()[0]+1:finalize_matches[-1].span()[1]]
            self.line_endings_correction()
            make_dst_folder(dir)
            with open(os.path.join(os.path.split(dir)[0], f'{self.name}_sliced{self.ext}'), "w") as f:
                f.write(self.lines)
            return True
        return False

