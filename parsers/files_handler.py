import re
import os
import json
import pickle
import shutil

from datetime import datetime


def load_file(path, load_by_line=True):
    name, ext = os.path.splitext(os.path.basename(path))
    ext = ext.lower()
    try:
        with open(path, 'r') as f:
            code = f.readlines() if load_by_line else str(f.read())
    except:
        with open(path, 'rb') as f:
            code = f.read().decode('latin1')
    return code, name, ext


def save_pkl(data, path):
    with open(f'{path}.pkl', 'wb') as f:
        pickle.dump(data, f)


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def write_to_json(data, path):
    if os.path.isfile(path):
        time = datetime.today().strftime("%m_%d_%y")
        path = re.sub("database\w*", f"database_info_{time}", path)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def files_walk(root_dir):
    fpaths = []
    for idx, (root, dirs, fnames) in enumerate(os.walk(root_dir)):
        fpaths += [os.path.join(root, fname) for fname in fnames]
    return fpaths


def get_repos(user_dir, id=0):
    return {id + offset: {'name': repo_name, 'path': os.path.join(user_dir, repo_name), 'programs': {}} for offset, repo_name in
            enumerate(os.listdir(user_dir))}


def make_dst_folder(dst):
    dstfolder = os.path.dirname(dst)
    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)


def start_idx_calc(src_origin):
    return len(os.path.join(os.getcwd(), src_origin)) + 1


def src_dst_prep(src, dst, src_origin):
    src = src[start_idx_calc(src_origin):]
    dst = os.path.join(dst, src)
    return src, dst


def copy_file(src, dst, src_origin):
    src, dst = src_dst_prep(src, dst, src_origin)
    make_dst_folder(dst)
    shutil.copy(os.path.join(src_origin, src), dst)