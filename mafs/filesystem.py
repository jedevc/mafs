import fuse

import os
import stat
import sys
import errno

from enum import Enum

import time
import itertools

from . import router
from . import file

class FileSystem(fuse.Operations):
    def __init__(self):
        self.routers = {method: router.Router() for method in Method}
        self.readers = {}
        self.writers = {}

        self.fh = 0

        self.timestamp = time.time()

    # Filesystem methods
    # ==================

    def getattr(self, path, fi=None):
        reader = self.routers[Method.READ].lookup(path)
        writer = self.routers[Method.WRITE].lookup(path)

        # FIXME: alert when reader and writer contradict each other
        if reader and reader.data or writer and writer.data:
            ftype = stat.S_IFREG
            permissions = 0
            if reader and reader.data:
                permissions |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            if writer and writer.data:
                permissions |= stat.S_IWUSR
        elif reader or writer:
            ftype = stat.S_IFDIR
            permissions = 0o755
        else:
            link = self.routers[Method.READLINK].lookup(path)
            if link and link.data:
                ftype = stat.S_IFLNK
                permissions = 0o755
            else:
                # cannot find in router
                raise fuse.FuseOSError(errno.ENOENT)

        uid, gid, _ = fuse.fuse_get_context()
        base = {
            'st_atime': self.timestamp,
            'st_ctime': self.timestamp,
            'st_mtime': self.timestamp,

            'st_gid': gid,
            'st_uid': uid,

            'st_mode': ftype | permissions,
            'st_nlink': 1,
            'st_size': 0
        }

        statter = self.routers[Method.STAT].lookup(path)
        if statter and statter.data:
            try:
                contents = statter.data(path, statter.parameters)
            except FileNotFoundError:
                raise fuse.FuseOSError(errno.ENOENT)

            if contents:
                return {**base, **contents}

        return base

    def readdir(self, path, fi):
        dirs = set(['.', '..'])

        ls = self.routers[Method.LIST].lookup(path)
        if ls and ls.data:
            contents = ls.data(path, ls.parameters)
            return itertools.chain(dirs, contents)
        else:
            for method in (Method.READ, Method.WRITE, Method.READLINK):
                contents = self.routers[method].list(path)
                if contents and contents.data:
                    return itertools.chain(dirs, contents.data)

        return dirs

    def readlink(self, path):
        result = self.routers[Method.READLINK].lookup(path)
        if result:
            return result.data(path, result.parameters)

    def truncate(self, path, length, fi=None):
        pass

    # File methods
    # ============

    def open(self, path, fi):
        reader = self.routers[Method.READ].lookup(path)
        writer = self.routers[Method.WRITE].lookup(path)

        success = False

        if fi.flags & os.O_RDONLY == os.O_RDONLY and reader and reader.data:
            callback, encoding = reader.data
            contents = callback(path, reader.parameters)

            if contents:
                self.readers[self.fh] = file.FileReader.create(contents, encoding)

            success = True

        if fi.flags & os.O_WRONLY == os.O_WRONLY and writer and writer.data:
            callback, encoding = writer.data
            contents = callback(path, writer.parameters)

            if contents:
                self.writers[self.fh] = file.FileWriter.create(contents, encoding)

            success = True

        if success:
            fi.fh = self.fh
            self.fh += 1
            fi.direct_io = True

            return 0
        else:
            return -1

    def read(self, path, length, offset, fi):
        if fi.fh in self.readers:
            return self.readers[fi.fh].read(length, offset)

    def write(self, path, data, offset, fi):
        if fi.fh in self.writers:
            return self.writers[fi.fh].write(data, offset)
        else:
            return len(data)

    def release(self, path, fi):
        if fi.fh in self.readers:
            reader = self.readers.pop(fi.fh)
            reader.release()

        if fi.fh in self.writers:
            writer = self.writers.pop(fi.fh)
            writer.release()

    # Callbacks
    # =========

    def onstat(self, path, callback):
        self.routers[Method.STAT].add(path, callback)

    def onread(self, path, callback, encoding='utf-8'):
        self.routers[Method.READ].add(path, (callback, encoding))

    def onwrite(self, path, callback, encoding='utf-8'):
        self.routers[Method.WRITE].add(path, (callback, encoding))

    def onreadlink(self, path, callback):
        self.routers[Method.READLINK].add(path, callback)

    def onlist(self, path, callback):
        self.routers[Method.LIST].add(path, callback)

class Method(Enum):
    STAT = 0
    READ = 1
    WRITE = 2
    READLINK = 3
    LIST = 4
