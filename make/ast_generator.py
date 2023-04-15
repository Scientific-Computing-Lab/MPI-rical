import os
import shutil

from datetime import datetime
from c_ast import ast

from logger import info


def init_folders(save_repo_outputs_dir, idx):
    save_outputs_dir = os.path.join(save_repo_outputs_dir, idx)
    fake_headers_path = os.path.join(save_outputs_dir, 'fake_headers')

    os.mkdir(save_outputs_dir)
    os.mkdir(fake_headers_path)
    return save_outputs_dir, fake_headers_path


def ast_generator(programs_db):
    count_success = 0
    count_failure = 0
    cur_time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    logger_path = fr'/home/nadavsc/LIGHTBITS/code2mpi/logger/ast_logger_{cur_time}.txt'
    with open(logger_path, 'w') as f:
        f.write('')

    for repo in programs_db.values():
        save_repo_outputs_dir = os.path.join(os.path.dirname(repo['programs']['0']), 'outputs')
        if os.path.exists(save_repo_outputs_dir):
            shutil.rmtree(save_repo_outputs_dir)
        os.mkdir(save_repo_outputs_dir)
        for idx, program_path in repo['programs'].items():
            print(program_path)
            fake_files = os.path.join(program_path, 'fake_files')
            fake_headers = os.path.join(program_path, 'fake_headers')
            if os.path.exists(fake_files):
                shutil.rmtree(fake_files)
            if os.path.exists(fake_headers):
                shutil.rmtree(fake_headers)
            save_outputs_dir, fake_headers_path = init_folders(save_repo_outputs_dir, idx)
            try:
                ast(origin_folder=program_path,
                    fake_headers_path=fake_headers_path,
                    save_dir=save_outputs_dir)
                count_success += 1
            except:
                cur_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                with open(logger_path, 'a') as f:
                    f.write(f'{cur_time}: {program_path}\n')
                count_failure += 1
            info(f'ast success: {count_success} | ast failure: {count_failure}')
    return


# 16/03/2023 22:13:55: ast success: 11,603 | ast failure: 3832 | fail ratio: 24.8%
# 18/03/2023 16:59:38: ast success: 11,150 | ast failure: 4285 | fail ratio: 27.7%
# 19/03/2023 04:48:33: ast success: 50,396 | ast failure: 23,462 | fail ratio: 31.7%
