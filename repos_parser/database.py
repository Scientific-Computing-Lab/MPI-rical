import os
import re
import json
import collections
import matplotlib.pyplot as plt

from repos_parser import REPOS_ORIGIN_DIR, PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_MPI_SLICED_DIR, EXTENSIONS, FORTRAN_EXTENSIONS
from repos_parser import write_to_json, load_json, get_repos
from files_parser import name_split, files_walk
from c_parse import repo_parser


from logger import set_logger, info

set_logger()


def db_origin_generate():
    database = {}
    repos_count = 0
    for id, user_name in enumerate(os.listdir(REPOS_ORIGIN_DIR)):
        database[id] = {'name': user_name, 'repos': {}}
        origin_user_dir = os.path.join(REPOS_ORIGIN_DIR, user_name)
        repos = {repo_id: {'name': repo_name, 'path': os.path.join(origin_user_dir, repo_name), 'types': {}}
                 for repo_id, repo_name in enumerate(os.listdir(origin_user_dir))}
        database[id]['repos'].update(repos)
        for repo_id, repo_details in repos.items():
            repo_types = database[id]['repos'][repo_id]['types']
            for fpath in files_walk(repo_details['path']):
                fname, ext = name_split(os.path.basename(fpath))
                if ext in EXTENSIONS:
                    repo_types[ext] = repo_types[ext] = (repo_types[ext] if ext in repo_types else 0) + 1
            repos_count += 1
            info(f'{repos_count}) Repo {repo_details["name"]} programs have been added to database')
    write_to_json(database, 'database_origin.json')


def db_programs_generate():
    database = {}
    for id, user_name in enumerate(os.listdir(PROGRAMS_MPI_DIR)):
        user_dir, origin_user_dir = os.path.join(PROGRAMS_MPI_DIR, user_name), os.path.join(REPOS_ORIGIN_DIR, user_name)
        database.update(get_repos(origin_user_dir, id))
        for repo_id, repo_details in get_repos(user_dir, id).items():
            for program_id, program_path in enumerate(os.listdir(repo_details['path'])):
                database[repo_id]['programs'][program_id] = os.path.join(repo_details['path'], program_path)
            info(f'{repo_id}) Repo {repo_details["name"]} programs have been added to database')
    write_to_json(database, 'database_programs.json')


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
    keys, values = sort_total_functions(total_functions(db))
    fig, ax = plt.subplots(1, 1)
    ax.set_title('Functions Distribution')
    ax.bar(keys[:30], values[:30], color='g')
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.show()


db_origin_generate()
