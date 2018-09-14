import stat

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
    def __init__(self, file_data, args):
        self.data = file_data

        read_contents = file_data.read_callback(*args)

        if self.data.read_callback:
            self.reader = FileReader.create(read_contents, self.data.read_encoding)
        else:
            self.reader = None

        self.writer = _FileWriter(file_data, args)

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

class _FileWriter:
    def __init__(self, file_data, args):
        self.func = None
        self.callback = None
        self.cache = []

        self.encoding = file_data.write_encoding

        if not file_data.write_callback:
            return

        try:
            func = file_data.write_callback(*args)
            if hasattr(func, '__call__'):
                self.func = func
        except TypeError:
            pass

        if not self.func:
            self.callback = lambda contents: file_data.write_callback(*args, contents)

    def write(self, data, offset):
        if self.func:
            # send data to function if available
            self.func(data, offset)
        elif self.callback:
            # otherwise, build up the cache
            self.cache[offset:offset + len(data)] = data

        return len(data)

    def release(self):
        if self.callback:
            # finalize the cache and send it to the callback
            if self.cache:
                self.callback(bytes(self.cache).decode(self.encoding))
