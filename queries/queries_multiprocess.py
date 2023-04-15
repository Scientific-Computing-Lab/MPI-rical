import os
import time
import shutil
import multiprocessing as mp

from multiprocessing import Pool
from datetime import datetime

from programs import init_folder, copy_files
from funcs_extract_reg import functions_in_file
from files_handler import load_file, copy_file, files_walk, write_to_json
from files_parse import Extractor, remove_comments, repo_parser, find_init_final, count_lines, mpi_in_line, openmp_in_line, is_include, comment_in_ranges

from config import PROGRAMS_MPI_DIR, REPOS_ORIGIN_DIR


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
                lines, init_match, finalize_matches = find_init_final(lines, rm_comments=True)
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
    dict = {'files': {}}
    for fpath in files_walk(repo['path']):
        lines, name, ext = load_file(fpath, load_by_line=False)
        lines = remove_comments(lines)  ## TODO: generalize to both C and Fortran
        if ext == '.h' or ext == '.c':
            functions = [func for func in functions_in_file(lines, ext)]
            if functions:
                dict['files'][fpath] = functions
                # dict['files'][fpath] = {'functions': {}}
                # dict['files'][fpath]['functions'] = functions
    counter_value = counter.value
    counter.increment(1)
    cur_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'{cur_time}: {counter_value} repos have been analyzed')
    queue.put({repo['path']: dict})


def functions_finder_listener(queue):
    database = {}
    while True:
        message = queue.get()
        if type(message) != str:
            database = {**database, **message}
        else:
            if message == '#done#':
                print('DONE')
                break
    print(f'Saving functions database to a json file...')
    write_to_json(database, 'database_functions.json')


def custom_error_callback(error):
    print(error)
    with open('errors.txt', 'w') as f:
        f.write(f'Got error: {error}')


def functions_finder_multiprocess(origin_db, n_cores=mp.cpu_count()-1):
    global counter
    counter = Counter()
    repos = []
    for user_id in origin_db.keys():
        for repo in origin_db[user_id]['repos'].values():
            repos.append(repo)
    print(f'Number of cores: {n_cores}')
    manager = mp.Manager()
    queue = manager.Queue()
    file_pool = mp.Pool(1)
    file_pool.apply_async(functions_finder_listener, (queue,))

    pool = mp.Pool(n_cores)
    jobs = []
    for repo in repos:
        job = pool.apply_async(functions_finder_task, (repo, queue), error_callback=custom_error_callback)
        jobs.append(job)

    for job in jobs:
        job.get()

    queue.put('#done#')
    time.sleep(20)
    pool.close()
    pool.join()


def program_division_task(user, functions_db):
    for repo_id, repo_details in user['repos'].items():
        repo_name, repo_dir = repo_details['name'], repo_details['path']
        programs_user_dir = os.path.join(PROGRAMS_MPI_DIR, user['name'])
        programs_repo_dir = os.path.join(programs_user_dir, repo_name)
        mains, repo_headers = repo_parser(REPOS_ORIGIN_DIR, repo_dir)
        if mains and not os.path.exists(programs_user_dir):
            os.makedirs(programs_user_dir)
        for main_path, main_name in mains.items():
            extractor = Extractor(main_path, main_name, repo_headers)
            extractor.extraction(main_path)
            headers_path = extractor.headers
            c_files_path = extractor.c_files(functions_db, repo_dir, headers_path)
            id, program_path = init_folder(programs_repo_dir)
            copy_files(id, repo_name, headers_path, c_files_path, program_path, main_path, repo_dir)
        counter.increment(1)
        cur_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"{cur_time}: {counter.value} Repos' Programs have been produced")


def program_division_multiprocess(origin_mpi_db, functions_db, n_cores=mp.cpu_count()-1):
    global counter
    counter = Counter()
    users = []
    for user in origin_mpi_db.values():
        if user['repos']:
            users.append(user)
    print(f'Number of cores: {n_cores}')

    pool = mp.Pool(n_cores)
    jobs = []
    for user in users:
        job = pool.apply_async(program_division_task, (user, functions_db), error_callback=custom_error_callback)
        jobs.append(job)

    for job in jobs:
        job.get()

    pool.close()
    pool.join()


def is_ast(program_path, fnames):
    ast_path = None
    code_path = None
    for fname in fnames:
        prefix = fname.split('_')[0]
        if prefix == 'ast':
            ast_path = os.path.join(program_path, fname)
        if prefix == 'proc':
            code_path = os.path.join(program_path, fname)
    return ast_path, code_path


def create_ast_db(repo):
    for program_id, program_path in repo['programs'].items():
        program_path = f'{os.path.dirname(program_path)}/outputs/{program_id}'
        ast_path, code_path = is_ast(program_path, os.listdir(program_path))
        if ast_path:
            dst_path = program_path[45:].split('/')
            dst_path.remove('outputs')
            dst_path = '_'.join(dst_path)
            dst_program_path = os.path.join(mpi_db, dst_path)
            dst_ast_path = os.path.join(dst_program_path, 'ast.pkl')
            dst_code_path = os.path.join(dst_program_path, 'code.c')

            os.makedirs(os.path.dirname(dst_ast_path), exist_ok=True)
            shutil.copy(src=ast_path, dst=dst_ast_path)
            shutil.copy(src=code_path, dst=dst_code_path)
            print(f'{counter.value}/50396 programs have been saved')
            counter.increment(1)


def create_ast_db_multiprocess(programs_db, n_cores=int(mp.cpu_count()-1)):
    global counter
    global mpi_db
    mpi_db = '/home/nadavsc/LIGHTBITS/code2mpi/DB/MPI'
    counter = Counter()
    repos = list(programs_db.values())
    print(f'Number of cores: {n_cores}')
    with Pool(n_cores) as p:
        p.map(create_ast_db, repos)

