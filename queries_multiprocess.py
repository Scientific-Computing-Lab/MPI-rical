import pdb
import multiprocessing as mp

from multiprocessing import Pool
from datetime import datetime

from repos_parser import write_to_json
from file_slice import find_init_final
from c_parse import functions_in_header, functions_in_implementation
from files_parser import load_file, files_walk, count_lines, mpi_in_line, openmp_in_line, is_include, del_comments, comment_in_ranges


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


def init_finalize_count_task(repo, queue):
    for program_id, program_path in repo['programs'].items():
        for fpath in files_walk(program_path):
            lines, name, ext = load_file(fpath, load_by_line=False)
            if ext == '.c':
                lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments=True)
                if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
                    counter.increment(1)
                    counter_value = counter.value
                    if counter_value % 500 == 0:
                        print(f'-----------------------{counter_value} Programs-----------------------')
                    num_lines = len(count_lines(lines))
                    init_finalize_lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
                    num_lines_init_finalize = len(count_lines(init_finalize_lines)) + 1
                    ratio = num_lines_init_finalize/num_lines
                    message = f'All lines: {num_lines}, Init-Finalize: {num_lines_init_finalize}, Ratio: {ratio:.2f}'
                    print(message)
                    queue.put(message)


def init_finalize_count_listener(queue):
    with open('init-finalize-stats.txt', 'a') as f:
        while True:
            message = queue.get()
            if message == '#done#':
                f.write(f'There are {counter.value} programs with Init-Finalize structure')
                break
            f.write(str(message) + '\n')
            f.flush()


def init_finalize_count_multiprocess(db, n_cores=int(mp.cpu_count()/2)):
    global counter
    counter = Counter()
    repos = list(db.values())
    print(f'Number of cores: {n_cores}')

    manager = mp.Manager()
    queue = manager.Queue()
    file_pool = mp.Pool(1)
    file_pool.apply_async(init_finalize_count_listener, (queue,))

    pool = mp.Pool(n_cores)
    jobs = []
    for repo in repos:
        job = pool.apply_async(init_finalize_count_task, (repo, queue))
        jobs.append(job)

    for job in jobs:
        job.get()

    queue.put('#done#')
    pool.close()
    pool.join()


def functions_finder_task(repo, queue):
    dict = {'path': repo['path'], 'headers': {}}
    for fpath in files_walk(repo['path']):
        lines, name, ext = load_file(fpath, load_by_line=False)
        lines = del_comments(lines, ext)
        if ext == '.h' and name not in dict['headers'].keys():
            header_functions = [f_header for f_header in functions_in_header(lines)]
            if header_functions:
                name = name + '.h'
                dict['headers'][name] = {}
            for idx in range(len(header_functions)):
                dict['headers'][name][idx] = header_functions[idx]
    counter.increment(1)
    cur_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'{cur_time}: {counter.value} repos have been analyzed')
    queue.put({repo['name']: dict})


def functions_finder_listener(queue):
    database = {}
    while True:
        message = queue.get()
        if type(message) != str:
            database = {**database, **message}
        else:
            if message == '#done#':
                break
    print(f'Saving functions database to a json file...')
    write_to_json(database, 'implementation_funcs.json')


def functions_finder_multiprocess(origin_db, n_cores=mp.cpu_count()-1):
    global counter
    counter = Counter()
    repos = []
    for user_id in origin_db.keys():
        for repo in origin_db[user_id]['repos'].values():
            repos.append(repo)
    repos = repos[:50]
    print(f'Number of cores: {n_cores}')
    manager = mp.Manager()
    queue = manager.Queue()
    file_pool = mp.Pool(1)
    file_pool.apply_async(functions_finder_listener, (queue,))

    pool = mp.Pool(n_cores)
    jobs = []
    for repo in repos:
        job = pool.apply_async(functions_finder_task, (repo, queue))
        jobs.append(job)

    for job in jobs:
        job.get()

    queue.put('#done#')
    pool.close()
    pool.join()

