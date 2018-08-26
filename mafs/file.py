from os import st

class FileData:
    def __init__(self, ftype=st.S_IFREG, permissions=0o644, encoding='utf-8'):
        self.read_callback = None
        self.write_callback = None

        self.ftype = ftype
        self.permissions = permissions

        self.encoding = encoding

    @property
    def mode(self):
        return self.ftype | self.permissions

    def onread(self, callback):
        self.read_callback = callback

    def onwrite(self, callback):
        self.write_callback = callback

class File:
    def __init__(self, file_data, args):
        self.file_data = file_data

        self.args = args

        self.contents = None
        self.cache = ''

        # TODO: move to read function
        if file_data.read_callback:
            contents = file_data.read_callback(*args)
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

    def write(self, data, offset):
        if self.file_data.write_callback:
            self.file_data.write_callback(data, *self.args)
            return len(data)
