import fuse

import os
from os import st
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
                mode = st.S_IFDIR | 0o755
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
            'st_size': 1
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
            return result.data.read_callback(path, result.parameters)

    # File methods
    # ============

    def open(self, path, fi):
        if self.router.lookup(path):
            fi.fh = self.fh
            self.fh += 1

            fi.direct_io = True
            return 0
        else:
            return -1

    def read(self, path, length, offset, fi):
        # TODO: move into self.open
        if fi.fh not in self.open_files:
            result = self.router.lookup(path)
            if result:
                self.open_files[fi.fh] = file.File(result.data, [path, result.parameters])
            else: return

        buf = self.open_files[fi.fh].read(length, offset)
        return buf

    def write(self, path, data, offset, fi):
        if fi.fh not in self.open_files:
            result = self.router.lookup(path)
            if result:
                self.open_files[fi.fh] = file.File(result.data, [path, result.parameters])
            else: return

        return self.open_files[fi.fh].write(data, offset)

    def release(self, path, fi):
        self.open_files.pop(fi.fh)

    def truncate(self, path, length, fh=None):
        pass

    # Callbacks
    # =========

    def onread(self, path, callback, encoding='utf-8'):
        result = self.router.lookup(path)
        if result and result.data:
            f = result.data
        else:
            f = file.FileData(encoding=encoding)
            self.router.add(path, f)

        f.onread(callback)

    def onreadlink(self, path, callback):
        result = self.router.lookup(path)
        if result and result.data:
            f = result.data
        else:
            f = file.FileData(ftype=st.S_IFLNK)
            self.router.add(path, f)

        f.onread(callback)

    def onwrite(self, path, callback):
        result = self.router.lookup(path)
        if result and result.data:
            f = result.data
        else:
            f = file.FileData()
            self.router.add(path, f)

        f.onwrite(callback)
