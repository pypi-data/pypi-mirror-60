import os,shutil,glob

def copy_files_to(files,dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for i,f in files:
        fn=os.path.basename(f)
        f2=dst+'/'+fn
        shutil.copy(f,f2)
def tranverse_files(dir,func):
    fs=glob.glob(dir+'/*')
    for f in fs:
        if os.path.isfile(f):
            func(f)
        elif os.path.isdir(f):
            tranverse_files(f,func)
def tranverse_dirs(dir,func):
    fs=glob.glob(dir+'/*')
    for f in fs:
        if os.path.isfile(f):
            pass
        elif os.path.isdir(f):
            func(f)
            tranverse_dirs(f,func)
