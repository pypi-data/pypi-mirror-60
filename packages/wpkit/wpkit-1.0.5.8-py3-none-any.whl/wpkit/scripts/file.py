import os,shutil,glob
from wpkit.basic import PowerDirPath
from wpkit.fsutil import copy_files_to
import fire
def catchfiles(dir,s):
    return PowerDirPath(dir).deepglob(s)
def cft(src,s,dst):
    fs=catchfiles(src,s)
    copy_files_to(fs,dst)

if __name__ == '__main__':
    fire.Fire()