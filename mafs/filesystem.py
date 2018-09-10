import fuse

import os
import stat
import sys
import errno

import time

from . import router
from . import file

class FileSystem(fuse.Operations):
    def __init__(self):
        self.router = router.Router()
        self.open_files = {}

        self.fh = 0

        self.timestamp = time.time()

    # Filesystem methods
    # ==================

    def getattr(self, path, fi=None):
        result = self.router.lookup(path)
        if result:
            if result.data:
                mode = result.data.mode
            else:
                mode = stat.S_IFDIR | 0o755
        else:
            raise fuse.FuseOSError(errno.ENOENT)

        uid, gid, _ = fuse.fuse_get_context()

        return {
            'st_atime': self.timestamp,
            'st_ctime': self.timestamp,
            'st_mtime': self.timestamp,

            'st_gid': gid,
            'st_uid': uid,

            'st_mode': mode,
            'st_nlink': 1,
            'st_size': 0
        }

    def readdir(self, path, fi):
        dirs = ['.', '..']
        contents = self.router.list(path)
        if contents:
            dirs.extend(contents.data)

        return dirs

    def readlink(self, path):
        result = self.router.lookup(path)
        if result:
            return result.data.get(path, result.parameters)

    def truncate(self, path, length, fi=None):
        pass

    # File methods
    # ============

    def open(self, path, fi):
        # forbid append operation
        if fi.flags & os.O_APPEND == os.O_APPEND:
            return -1

        result = self.router.lookup(path)
        if result and result.data:
            fi.fh = self.fh
            self.fh += 1
            fi.direct_io = True

            self.open_files[fi.fh] = file.File(result.data, [path, result.parameters])

            return 0
        else:
            return -1

    def read(self, path, length, offset, fi):
        return self.open_files[fi.fh].read(length, offset)

    def write(self, path, data, offset, fi):
        return self.open_files[fi.fh].write(data, offset)

    def release(self, path, fi):
        file = self.open_files.pop(fi.fh)
        file.release()

    # Callbacks
    # =========

    def _create_file(self, path, *args, **kwargs):
        result = self.router.lookup(path)
        if result and result.data:
            return result.data
        else:
            fd = file.FileData(*args, **kwargs)
            self.router.add(path, fd)
            return fd

    def onread(self, path, callback, encoding='utf-8'):
        f = self._create_file(path)
        f.onread(callback, encoding)

    def onreadlink(self, path, callback):
        f = self._create_file(path, ftype=stat.S_IFLNK)
        f.onget(callback)

    def onwrite(self, path, callback, encoding='utf-8'):
        f = self._create_file(path)
        f.onwrite(callback, encoding)
