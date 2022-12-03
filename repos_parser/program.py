import os
from repos_parser import PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_ORIGIN_DIR, copy_file

from logger import info


class Program:
    def __init__(self, program, repo):
        self.main_name, self.main_path = program['main']['name'], program['main']['path']
        self.headers_path = program['headers']
        self.repo_name, self.repos_dir = repo.name, repo.repos_dir
        self.id, self.path = self.init_folder()

    def init_folder(self):
        programs_names = os.listdir(PROGRAMS_MPI_DIR)
        if programs_names:
            id = int(programs_names[-1].split('_')[1]) + 1
        else:
            id = 0
        path = os.path.join(PROGRAMS_MPI_DIR, f'program_{id}')
        if not os.path.exists(path):
            os.makedirs(path)
        copy_file(src=self.main_path, dst=path, src_repo=REPOS_ORIGIN_DIR)
        for header_path in self.headers_path:
            copy_file(src=header_path, dst=path, src_repo=REPOS_ORIGIN_DIR)
        info(f'PROGRAM {id} has been created - Origin repo: {self.repo_name}')
        return id, path

