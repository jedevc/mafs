import os
import errno
import fuse
import stat
import inspect
import time
import itertools

class FileReader:
    def create(contents, encoding):
        for reader in [FileReader.Raw, FileReader.File, FileReader.Function, FileReader.Iterable]:
            r = reader.create(contents, encoding)
            if r:
                return r

        raise FileError(str(contents) + ' cannot be used as a file reader')

    class Raw:
        @staticmethod
        def create(contents, encoding):
            try:
                return FileReader.Raw(contents.encode(encoding))
            except AttributeError:
                return None

        def __init__(self, contents):
            self.contents = contents

        def read(self, length, offset):
            return self.contents[offset:offset + length]

        def release(self):
            pass

    class File:
        @staticmethod
        def create(contents, encoding):
            if hasattr(contents, 'read') and hasattr(contents, 'write'):
                return FileReader.File(contents, encoding)

        def __init__(self, file, encoding = None):
            self.file = file
            self.encoding = encoding

        def read(self, length, offset):
            self.file.seek(offset)
            data = self.file.read(length)
            if self.encoding:
                data = data.encode(self.encoding)
            return data

        def release(self):
            self.file.close()

    class Function:
        @staticmethod
        def create(contents, encoding):
            if hasattr(contents, '__call__') and _arg_count(contents) == 2:
                return FileReader.Function(contents, encoding)

        def __init__(self, func, encoding):
            self.func = func
            self.encoding = encoding

        def read(self, length, offset):
            return self.func(length, offset)

        def release(self):
            pass

    class Iterable:
        @staticmethod
        def create(contents, encoding):
            try:
                return FileReader.Iterable(iter(contents), encoding)
            except TypeError:
                return None

        def __init__(self, iterable, encoding):
            self.generator = iterable
            self.cache = bytes()
            self.encoding = encoding

        def read(self, length, offset):
            # read data into cache if provided by an iterable
            while self.generator and len(self.cache) < offset + length:
                try:
                    part = next(self.generator)
                    if self.encoding:
                        part = part.encode(self.encoding)
                    self.cache += part
                except StopIteration:
                    self.generator = None

            # provide requested data from the cache
            return self.cache[offset:offset + length]

        def release(self):
            pass


class FileWriter:
    def create(contents, encoding):
        for writer in [FileWriter.Function, FileWriter.Full, FileWriter.File]:
            w = writer.create(contents, encoding)
            if w:
                return w

        raise FileError(str(contents) + ' cannot be used as a file writer')

    class Function:
        def create(contents, encoding):
            if hasattr(contents, '__call__') and _arg_count(contents) == 2:
                return FileWriter.Function(contents)

        def __init__(self, func):
            self.func = func

        def write(self, data, offset):
            self.func(data, offset)
            return len(data)

        def release(self):
            pass

    class Full:
        def create(contents, encoding):
            if hasattr(contents, '__call__') and _arg_count(contents) == 1:
                return FileWriter.Full(contents, encoding)

        def __init__(self, callback, encoding):
            self.callback = callback
            self.encoding = encoding

            self.cache = []

        def write(self, data, offset):
            # extend cache size
            ldiff = len(self.cache) - len(data)
            if ldiff < 0:
                self.cache.extend(itertools.count(-1, ldiff))

            self.cache[offset:offset + len(data)] = data
            return len(data)

        def release(self):
            try:
                self.callback(bytes(self.cache).decode(self.encoding))
            except ValueError:
                raise FuseOSError(errno.EIO)

    class File:
        def create(contents, encoding):
            if hasattr(contents, 'read') and hasattr(contents, 'write'):
                return FileWriter.File(contents, encoding)

        def __init__(self, file, encoding):
            self.file = file
            self.encoding = encoding

        def write(self, data, offset):
            self.file.seek(offset)
            if self.encoding:
                data = data.decode(self.encoding)
            return self.file.write(data)

        def release(self):
            self.file.close()

class FileError(Exception):
    pass

def _arg_count(func):
    return len(inspect.signature(func).parameters)
