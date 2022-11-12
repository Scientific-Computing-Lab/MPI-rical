import os
import re
import shutil
import json


from repos_parser import REPOS_ORIGIN_DIR, REPOS_MPI_DIR, EXTENSIONS, FORTRAN_EXTENSIONS, START_IDX, write_to_json


def copy_file(src, dst, MPI_functions):
    '''
    copy src file to a given destination (preserve the file structure)
    '''
    src = src[START_IDX:]
    dst = os.path.join(dst, src)
    dstfolder = os.path.dirname(dst)

    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)

    shutil.copy(os.path.join(REPOS_ORIGIN_DIR, src), dst)
    with open(f'{dst}.json', "w") as f:
        json.dump(MPI_functions, f, indent=4)


def MPI_func_included(contents):
    funcs_count = {}
    MPI_funcs = re.findall('MPI_\w*', contents)  # \S* for all the function
    for func in MPI_funcs:
        funcs_count[func] = (funcs_count[func] if func in funcs_count else 0) + 1
    return funcs_count


def MPI_included(line, language='c'):
    line = str(line).lower()
    if language == 'c':
        return '#include' in line and 'mpi.h' in line
    return 'include' in line and 'mpif.h' in line


def update_type_counter(ext):
    type_counter[ext] = (type_counter[ext] if ext in type_counter else 0) + 1


def scan_dir(root_dir):
    for idx, (root, dirs, files) in enumerate(os.walk(root_dir)):
        for file_name in files:
            extension = os.path.splitext(file_name)[1].lower()

            if extension in EXTENSIONS:
                path = os.path.join(root, file_name)
                with open(path, 'rb') as f:
                    contents = str(f.read())

                MPI_funcs = MPI_func_included(contents)
                if MPI_funcs:
                    # write_to_json(data=MPI_funcs, path=repos_mpi_dir)
                    update_type_counter(extension)
                    copy_file(path, REPOS_MPI_DIR, MPI_funcs)
                    break

        if idx % 10 ** 3 == 0:
            print(f'{idx}) {type_counter}')



type_counter = {}
for dir in os.listdir(REPOS_ORIGIN_DIR):
    scan_dir(os.path.join(REPOS_ORIGIN_DIR, dir))
with open('extractor_logger.txt', 'w') as f:
    f.write(str(type_counter))