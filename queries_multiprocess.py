import multiprocessing as mp

from multiprocessing import Pool

from files_parser import mpi_in_line, openmp_in_line, is_include, files_walk
from logger import set_logger, info


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
    info(f'Number of cores: {n_cores}')
    with Pool(n_cores) as p:
        p.map(openmp_mpi_count_task, repos)


