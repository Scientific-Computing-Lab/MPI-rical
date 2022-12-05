import os
from repos_parser import PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_ORIGIN_DIR, copy_file

from logger import info


class Program:
    def __init__(self, program, user, repo_name, repo_dir):
        self.main_name, self.main_path = program['main']['name'], program['main']['path']
        self.headers_path = program['headers']
        self.repo_name = repo_name
        self.repo_dir = repo_dir
        self.programs_user_dir = user.programs_user_dir
        self.programs_repo_dir = os.path.join(self.programs_user_dir, repo_name)
        self.user_name, self.users_dir, self.user_dir = user.name, user.users_dir, user.user_dir
        self.id, self.path = self.init_folder()
        self.copy_files()

    def copy_files(self):
        copy_file(src=self.main_path, dst=self.path, src_origin=self.repo_dir)
        for header_path in self.headers_path:
            copy_file(src=header_path, dst=self.path, src_origin=self.repo_dir)
        info(f'PROGRAM {self.id} has been created - Origin repo: {self.user_name}')

    def init_folder(self):
        if not os.path.exists(self.programs_repo_dir):
            os.makedirs(self.programs_repo_dir)
        programs_names = os.listdir(self.programs_repo_dir)
        if programs_names:
            id = int(programs_names[-1].split('_')[1]) + 1
        else:
            id = 0
        path = os.path.join(os.path.join(self.programs_repo_dir, f'program_{id}'))
        os.makedirs(path)
        return id, path

