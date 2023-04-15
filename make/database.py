import os
import collections
import matplotlib.pyplot as plt

from files_handler import files_walk, write_to_json, get_repos, load_json
from files_parse import repo_parser, repo_mpi_include, name_split
from config import REPOS_ORIGIN_DIR, PROGRAMS_MPI_DIR, REPOS_MPI_DIR, MPI_DIR, MPI_SERIAL_DIR, EXTENSIONS, FORTRAN_EXTENSIONS
from logger import set_logger, info

set_logger()


def db_origin_generate(mpi_only=False):
    database = {}
    repos_count = 0
    for id, user_name in enumerate(os.listdir(REPOS_ORIGIN_DIR)):
        database[id] = {'name': user_name, 'repos': {}}
        origin_user_dir = os.path.join(REPOS_ORIGIN_DIR, user_name)
        repos = {repo_id: {'name': repo_name, 'path': os.path.join(origin_user_dir, repo_name), 'types': {}}
                 for repo_id, repo_name in enumerate(os.listdir(origin_user_dir)) if not mpi_only or repo_mpi_include(os.path.join(origin_user_dir, repo_name))}
        database[id]['repos'].update(repos)
        for repo_id, repo_details in repos.items():
            repo_types = database[id]['repos'][repo_id]['types']
            for fpath in files_walk(repo_details['path']):
                fname, ext = name_split(os.path.basename(fpath))
                if ext in EXTENSIONS:
                    repo_types[ext] = (repo_types[ext] if ext in repo_types else 0) + 1
            repos_count += 1
            info(f'{repos_count}) Repo {repo_details["name"]} has been added to database')
    write_to_json(database, 'database_origin.json')


def db_programs_generate():
    database = {}
    id = 0
    for user_name in os.listdir(PROGRAMS_MPI_DIR):
        user_dir, origin_user_dir = os.path.join(PROGRAMS_MPI_DIR, user_name), os.path.join(REPOS_ORIGIN_DIR, user_name)
        repos = get_repos(user_dir, id)
        database.update(repos)
        for repo_id, repo_details in repos.items():
            programs_names = os.listdir(repo_details['path'])
            if 'outputs' in programs_names:
                programs_names.remove('outputs')
            for program_id, program_path in enumerate(programs_names):
                database[repo_id]['programs'][program_id] = os.path.join(repo_details['path'], program_path)
            info(f'{repo_id}) Repo {repo_details["name"]} programs have been added to database')
        id += len(repos)
    write_to_json(database, 'database_programs.json')


def db_mpi_generate():
    database = {}
    for idx, program_name in enumerate(os.listdir(MPI_DIR)):
        program_dir = os.path.join(MPI_DIR, program_name)
        ast_path = os.path.join(program_dir, 'ast.pkl')
        code_path = os.path.join(program_dir, 'code.c')
        database.update({program_name: {'ast': ast_path, 'code': code_path}})
        info(f'{idx}) programs have been added to database')
    write_to_json(database, 'database_mpi.json')


def db_serial_mpi_generate():
    database = {}
    for idx, program_name in enumerate(os.listdir(MPI_SERIAL_DIR)):
        program_dir = os.path.join(MPI_SERIAL_DIR, program_name)
        ast_path = os.path.join(program_dir, 'ast.pkl')
        code_path = os.path.join(program_dir, 're_code.c')
        mpi_code_path = os.path.join(program_dir, 'mpi_re_code.c')
        database.update({program_name: {'ast': ast_path, 'code': code_path, 'mpi_code': mpi_code_path}})
        info(f'{idx}) programs have been added to database')
    write_to_json(database, '/home/nadavsc/LIGHTBITS/code2mpi/DB/database_serial_mpi.json')


def functions_chain_counter(db):
    chain_funcs = {}
    for user_name, info in db.items():
        for script_name, script_info in info['scripts'].items():
            funcs = '->'.join(script_info['funcs'].keys()).lower()
            chain_funcs[funcs] = (chain_funcs[funcs] if funcs in chain_funcs else 0) + 1
    return chain_funcs


def total_script_types(db):
    counter = collections.Counter()
    for value in db.values():
        counter.update(value['types'])
    return dict(counter)


def sort_total_functions(total_functions):
    return zip(*dict(sorted(total_functions.items(), key=lambda item: item[1], reverse=True)).items())


def total_functions(db):
    counter = collections.Counter()
    for value in db.values():
        for script in value['scripts'].values():
            counter.update(script['funcs'])
    return dict(counter)


def draw_functions_hist(db):
    keys, values = sort_total_functions(db)  # if functions by reg: total_functions(db)
    fig, ax = plt.subplots(1, 1)
    ax.set_title('Functions Distribution')
    ax.bar(keys[:30], values[:30], color='g')
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.show()

# db_serial_mpi_generate()

# db = load_json(os.path.join('/home/nadavsc/LIGHTBITS/code2mpi/stats', 'mpi_funcs_per_file.json'))
# draw_functions_hist(db)

# training
# eval_loss = [1.5359086990356445, 1.4974662065505981, 1.487998127937317, 1.4845249652862549, 1.4827420711517334, 1.4808318614959717, 1.4797585010528564, 1.479016900062561, 1.478766918182373, 1.4786592721939087]
# eval_accuracy = [0.10205314009661835, 0.10909822866344605, 0.11493558776167472, 0.1143317230273752, 0.11332528180354268, 0.11694847020933978, 0.11694847020933978, 0.11372785829307569, 0.11634460547504026, 0.11694847020933978]
