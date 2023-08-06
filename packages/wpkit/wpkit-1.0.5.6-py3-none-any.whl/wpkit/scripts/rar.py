import fire
import rarfile
def unrar(src,dst):
    import os
    src=rarfile.RarFile(src)
    if not os.path.exists(dst):
        os.makedirs(dst)
    src.extractall(dst)
def rarx(src=None,dst=None):
    from wpkit.basic import PowerDirPath
    import os
    src = src or './'
    src= PowerDirPath(src)
    if src.isdir():
        dst = dst or src
        dst=PowerDirPath(dst)
        fs=src.glob('*.rar')
        for i,f in enumerate(fs):
            dn=f.basename()[:-4]
            dp=dst.join_path(dn)
            unrar(f,dp)
            print(i,f,dp)
    elif src.isfile():
        assert src.endswith('.rar')
        dst= dst or src[:-4]
        unrar(src,dst)
        print(src,dst)
    print('finished.')

if __name__ == '__main__':
    fire.Fire()