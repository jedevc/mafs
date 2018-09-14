import os
import stat
import inspect

class FileData:
    def __init__(self, ftype=stat.S_IFREG):
        self.get_callback = None

        self.read_callback = None
        self.read_encoding = None

        self.write_callback = None
        self.write_encoding = None

        self.ftype = ftype

    @property
    def mode(self):
        permissions = 0
        if self.ftype == stat.S_IFREG:
            if self.read_callback:
                permissions |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            if self.write_callback:
                permissions |= stat.S_IWUSR
            return self.ftype | permissions
        else:
            return self.ftype | 0o644

    def get(self, *args):
        return self.get_callback(*args)

    def onget(self, callback):
        self.get_callback = callback

    def onread(self, callback, encoding='utf-8'):
        self.read_callback = callback
        self.read_encoding = encoding

    def onwrite(self, callback, encoding='utf-8'):
        self.write_callback = callback
        self.write_encoding = encoding

class File:
    def __init__(self, file_data, args, flags):
        self.data = file_data

        if self.data.read_callback and flags & os.O_RDONLY == os.O_RDONLY:
            read_contents = self.data.read_callback(*args)
            self.reader = FileReader.create(read_contents, self.data.read_encoding)
        else:
            self.reader = None

        if self.data.write_callback and flags & os.O_WRONLY == os.O_WRONLY:
            write_contents = self.data.write_callback(*args)
            self.writer = FileWriter.create(write_contents, self.data.write_encoding)
        else:
            self.writer = None

    def read(self, length, offset):
        if self.reader:
            return self.reader.read(length, offset)

    def write(self, data, offset):
        if self.writer:
            return self.writer.write(data, offset)

    def release(self):
        if self.reader:
            self.reader.release()
        if self.writer:
            self.writer.release()

class FileReader:
    def create(contents, encoding):
        for reader in [FileReader.Raw, FileReader.File, FileReader.Function, FileReader.Iterable]:
            r = reader.create(contents, encoding)
            if r:
                return r

    class File:
        @staticmethod
        def create(contents, encoding):
            if hasattr(contents, '__read__') and hasattr(contents, '__write__'):
                return FileReader.File(contents, encoding)

        def __init__(self, file, encoding = None):
            self.file = file
            self.encoding = encoding

        def read(self, length, offset):
            self.file.seek(offset)
            data = self.file.read(length)
            if self.encoding:
                data = self.encode(self.encoding)
            return data

        def release(self):
            self.file.close()

    class Function:
        @staticmethod
        def create(contents, encoding):
            if hasattr(contents, '__call__'):
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

class FileWriter:
    def create(contents, encoding):
        for writer in [FileWriter.Function, FileWriter.Full]:
            w = writer.create(contents, encoding)
            if w:
                return w

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
            self.cache[offset:offset + len(data)] = data
            return len(data)

        def release(self):
            self.callback(bytes(self.cache).decode(self.encoding))

def _arg_count(func):
    return len(inspect.signature(func).parameters)
