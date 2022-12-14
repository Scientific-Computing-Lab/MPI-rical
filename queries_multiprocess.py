import multiprocessing as mp

from multiprocessing import Pool

from files_parser import load_file, files_walk, count_lines, mpi_in_line, openmp_in_line, is_include
from file_slice import find_init_final, comment_in_ranges


class Counter(object):
    def __init__(self):
        self.val = mp.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value


def openmp_mpi_count_task(repo):
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
                print(f'{counter.value} programs have been found')
                counter.increment(1)
                break


def openmp_mpi_count_multiprocess(db, n_cores=int(mp.cpu_count()-1)):
    global counter
    counter = Counter()
    repos = list(db.values())
    print(f'Number of cores: {n_cores}')
    with Pool(n_cores) as p:
        p.map(openmp_mpi_count_task, repos)


def init_finalize_count_task(repo):
    for program_id, program_path in repo['programs'].items():
        for fpath in files_walk(program_path):
            lines, name, ext = load_file(fpath, load_by_line=False)
            if ext == '.c':
                lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments=True)
                if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
                    counter.increment(1)
                    num_lines = len(count_lines(lines))
                    init_finalize_lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
                    num_lines_init_finalize = len(count_lines(init_finalize_lines)) + 1
                    ratio = num_lines_init_finalize/num_lines
                    print(f'{counter.value} Init-Finalize programs\nAll lines: {num_lines}, Init-Finalize: {num_lines_init_finalize}, Ratio: {ratio:.2f}\n')


def init_finalize_count_multiprocess(db, n_cores=int(mp.cpu_count()-1)):
    global counter
    counter = Counter()
    repos = list(db.values())
    print(f'Number of cores: {n_cores}')
    with Pool(n_cores) as p:
        p.map(init_finalize_count_task, repos)

