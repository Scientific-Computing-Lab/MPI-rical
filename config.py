import yaml

verbose = 2
with open('/home/nadavsc/LIGHTBITS/code2mpi/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    exclude_headers = config['exclude_headers']
    REPOS_ORIGIN_DIR = config['REPOS_ORIGIN_DIR']
    REPOS_MPI_DIR = config['REPOS_MPI_DIR']
    REPOS_MPI_SLICED_DIR = config['REPOS_MPI_SLICED_DIR']
    PROGRAMS_MPI_DIR = config['PROGRAMS_MPI_DIR']
    EXTENSIONS = config['EXTENSIONS']
    FORTRAN_EXTENSIONS = config['FORTRAN_EXTENSIONS']