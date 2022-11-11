import os

repos_dir = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
repos_mpi_dir = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
extentions = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
fortran_extentions = ['.f', '.f77', '.f90', '.f95', '.f03']
start_idx = len(os.path.join(os.getcwd(), repos_dir)) + 1
