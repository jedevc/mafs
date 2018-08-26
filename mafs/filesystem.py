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
        if fi.fh not in self.open_files:
            result = self.router.lookup(path)
            if result:
                self.open_files[fi.fh] = File(result.data, [path, result.parameters])
            else: return

        buf = self.open_files[fi.fh].read(length, offset)
        return buf

    def release(self, path, fi):
        self.open_files.pop(fi.fh)

    # Callbacks
    # =========

    def onread(self, path, callback, encoding='utf-8'):
        f = FileData(callback, encoding=encoding)
        self.router.add(path, f)

    def onreadlink(self, path, callback):
        f = FileData(callback, st.S_IFLNK)
        self.router.add(path, f)

class FileData:
    def __init__(self, callback, ftype=st.S_IFREG, permissions=0o644, encoding='utf-8'):
        self.callback = callback

        self.ftype = ftype
        self.permissions = permissions

        self.encoding = encoding

    @property
    def mode(self):
        return self.ftype | self.permissions

class File:
    def __init__(self, file_data, args):
        self.file_data = file_data

        contents = file_data.callback(*args)
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
                if self.file_data.encoding:
                    part = part.encode(self.file_data.encoding)
                self.cache += part
            except StopIteration:
                self.contents = None

        return self.cache[offset:offset + length]
