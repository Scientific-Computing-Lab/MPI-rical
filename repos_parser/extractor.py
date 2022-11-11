import os
import re
import shutil
import json


from repos_parser import repos_dir, repos_mpi_dir, extentions, fortran_extentions, start_idx


def copy_file(src, dst):
    '''
    copy src file to a given destination (preserve the file structure)
    '''
    src = src[start_idx:]
    dst = os.path.join(dst, src)
    dstfolder = os.path.dirname(dst)

    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)

    shutil.copy(os.path.join(repos_dir, src), dst)


def MPI_included(line, language='c'):
    line = str(line).lower()
    if language == 'c':
        return '#include' in line and 'mpi.h' in line
    return 'include' in line and 'mpif.h' in line


def scan_dir(root_dir):
    for idx, (root, dirs, files) in enumerate(os.walk(root_dir)):
        for file_name in files:
            copy = False
            ext = os.path.splitext(file_name)[1].lower()

            if ext in extentions:
                with open(f'{root}/{file_name}', 'rb') as f:
                    for line in f:
                        if MPI_included(line, 'c' if ext not in fortran_extentions else 'f'):
                            copy = True
                            result[ext] = (result[ext] if ext in result else 0) + 1

                        if copy:
                            copy_file(os.path.join(root, file_name), repos_mpi_dir)
                            break

        if idx % 10 ** 3 == 0:
            print(f'{idx}) {result}')


result = {}
for dir in os.listdir(repos_dir):
    scan_dir(os.path.join(repos_dir, dir))
with open('extractor_logger.txt', 'w') as f:
    f.write(str(result))