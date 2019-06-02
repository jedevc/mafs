import mafs

import os.path
import pathlib

fs = mafs.MagicFS()


def prefix(f):
    PREFIX = str(pathlib.Path.home())
    return os.path.join(PREFIX, f.strip('/'))


@fs.read('*file', encoding=None)
def read(path, ps):
    print('read', path)
    return open(prefix(path), 'rb')


@fs.write('*file', encoding=None)
def write(path, ps):
    print('write', path)
    return open(prefix(path), 'wb')


@fs.stat('*file')
def stat(path, ps):
    print('stat', path)
    stat = os.stat(prefix(path))

    return {
        'st_mode': stat.st_mode,
        'st_nlink': stat.st_nlink,
        'st_uid': stat.st_uid,
        'st_gid': stat.st_gid,
        'st_size': stat.st_size,
        'st_atime': stat.st_atime,
        'st_mtime': stat.st_mtime,
        'st_ctime': stat.st_ctime
    }


@fs.list('/')
@fs.list('*file')
def list(path, ps):
    print('list', path)
    return os.listdir(prefix(path))


fs.run()
