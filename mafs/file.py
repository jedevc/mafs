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
        self.file_data = file_data

        self.args = args

        self.reader = _FileReader(file_data, args)
        self.writer = _FileWriter(file_data, args)

    def read(self, length, offset):
        return self.reader.read(length, offset)

    def write(self, data, offset):
        return self.writer.write(data, offset)

    def release(self):
        self.reader.release()
        self.writer.release()

class _FileReader:
    def __init__(self, file_data, args):
        self.contents = None
        self.cache = bytes()
        self.encoding = file_data.read_encoding

        if not file_data.read_callback:
            return

        contents = file_data.read_callback(*args)
        try:
            # raw string
            self.cache = contents.encode(self.encoding)
        except AttributeError:
            # generator or other iterable
            self.contents = iter(contents)

    def read(self, length, offset):
        # read data into cache if provided by an iterable
        while self.contents and len(self.cache) < offset + length:
            try:
                part = next(self.contents)
                if self.encoding:
                    part = part.encode(self.encoding)
                self.cache += part
            except StopIteration:
                self.contents = None

        # provide requested data from the cache
        return self.cache[offset:offset + length]

    def release(self):
        pass

class _FileWriter:
    def __init__(self, file_data, args):
        self.contents = None
        self.callback = None
        self.cache = []

        self.encoding = file_data.write_encoding

        if not file_data.write_callback:
            return

        try:
            self.contents = file_data.write_callback(*args)
            next(self.contents)
        except TypeError:
            self.callback = lambda contents: file_data.write_callback(*args, contents)

    def write(self, data, offset):
        if self.contents:
            # send data into generator if available
            if self.encoding:
                data = data.decode(self.encoding)
            self.contents.send((data, offset))
        elif self.callback:
            # otherwise, build up the cache
            self.cache[offset:offset + len(data)] = data

        return len(data)

    def release(self):
        if self.contents:
            # close generator if available
            self.contents.close()
        elif self.callback:
            # otherwise finalize the cache and send it to the callback
            if self.cache:
                self.callback(bytes(self.cache).decode(self.encoding))
