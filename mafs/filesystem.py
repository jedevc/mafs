import fuse

import os
from os import st
import sys
import errno

import time

from . import router

class FileSystem(fuse.Operations):
    def __init__(self):
        self.router = router.Router()
        self.contents = {}

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
            return result.data.callback(path, result.parameters)

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
        if fi.fh not in self.contents:
            result = self.router.lookup(path)
            if result:
                self.contents[fi.fh] = result.data.open(path, result.parameters)
            else: return

        buf = self.contents[fi.fh].read(length, offset)
        return buf

    def release(self, path, fi):
        self.contents.pop(fi.fh)

    # Callbacks
    # =========

    def onread(self, path, callback, encoding='utf-8'):
        f = File(callback, encoding=encoding)
        self.router.add(path, f)

    def onreadlink(self, path, callback):
        f = File(callback, st.S_IFLNK)
        self.router.add(path, f)

class File:
    def __init__(self, callback, ftype=st.S_IFREG, permissions=0o644, encoding='utf-8'):
        self.callback = callback

        self.ftype = ftype
        self.permissions = permissions

        self.encoding = encoding

    @property
    def mode(self):
        return self.ftype | self.permissions

    def open(self, *args):
        return OpenFile(self.callback, self.ftype, self.permissions, self.encoding, args)

class OpenFile(File):
    def __init__(self, callback, ftype, permissions, encoding, args):
        super().__init__(callback, ftype, permissions, encoding)

        contents = self.callback(*args)
        try:
            self.contents = iter(contents)
            self.cache = bytes()
        except TypeError:
            self.cache = self.contents
            self.contents = None

    def read(self, length, offset):
        while self.contents and len(self.cache) < offset + length:
            try:
                part = next(self.contents)
                if self.encoding:
                    part = part.encode(self.encoding)
                self.cache += part
            except StopIteration:
                self.contents = None

        return self.cache[offset:offset + length]
