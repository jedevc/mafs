import fuse

import os
import sys
import errno

import time

from . import router

class FileSystem(fuse.Operations):
    def __init__(self):
        self.router = router.Router()

        self.fh = 0
        self.contents = {}

        self.timestamp = time.time()

    # Filesystem methods
    # ==================

    # def access(self, path, mode): pass
    # def chmod(self, path, mode): pass
    # def chown(self, path, uid, gid): pass

    def getattr(self, path, fi=None):
        result = self.router.lookup(path)
        if result:
            if result.data:
                mode = os.st.S_IFREG | 0o660
            else:
                mode = os.st.S_IFDIR | 0o660
        else:
            raise fuse.FuseOSError(errno.ENOENT)

        return {
            'st_atime': self.timestamp,
            'st_ctime': self.timestamp,
            'st_mtime': self.timestamp,

            'st_gid': os.getgid(),
            'st_uid': os.getuid(),

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

    # def readlink(self, path): pass
    # def mknod(self, path, mode, dev): pass
    # def rmdir(self, path): pass
    # def mkdir(self, path, mode): pass
    # def statfs(self, path): pass
    # def unlink(self, path): pass
    # def symlink(self, name, target): pass
    # def rename(self, old, new): pass
    # def link(self, target, name): pass
    # def utimens(self, path, times=None): pass

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

    # def create(self, path, mode, fi=None): pass

    def read(self, path, length, offset, fi):
        if fi.fh not in self.contents:
            result = self.router.lookup(path)
            if result:
                reader = Reader(result.data(path, result.parameters))
                self.contents[fi.fh] = reader
            else: return

        buf = self.contents[fi.fh].read(length, offset)
        if buf:
            return buf
        else:
            self.contents.pop(fi.fh)

    # def write(self, path, buf, offset, fi): pass
    # def truncate(self, path, length, fi=None): pass
    # def flush(self, path, fi): pass
    # def release(self, path, fi): pass
    # def fsync(self, path, fdatasync, fi): pass

    # Callbacks
    # =========

    def onread(self, path, callback):
        self.router.add(path, callback)

class Reader:
    def __init__(self, contents):
        try:
            self.contents = iter(contents)
            self.cache = bytes()
        except TypeError:
            self.cache = self.contents
            self.contents = None

    def read(self, length, offset):
        while self.contents and len(self.cache) < offset + length:
            try:
                self.cache += next(self.contents).encode('utf-8')
            except StopIteration:
                self.contents = None

        return self.cache[offset:offset + length]
