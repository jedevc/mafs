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

        if file_data.read_callback:
            contents = file_data.read_callback(*args)
            self.contents = iter(contents)
            self.cache = bytes()

        if file_data.write_callback:
            self.write_contents = file_data.write_callback(*args)
            next(self.write_contents)

    def read(self, length, offset):
        while self.contents and len(self.cache) < offset + length:
            try:
                part = next(self.contents)
                if self.file_data.read_encoding:
                    part = part.encode(self.file_data.read_encoding)
                self.cache += part
            except StopIteration:
                self.contents = None

        return self.cache[offset:offset + length]

    def write(self, data, offset):
        if self.file_data.write_callback:
            if self.file_data.write_encoding:
                data = data.decode(self.file_data.write_encoding)

            self.write_contents.send((data, offset))

        return len(data)

    def release(self):
        if self.file_data.write_callback:
            self.write_contents.close()
