from os import st

class FileData:
    def __init__(self, ftype=st.S_IFREG, permissions=0o644):
        self.get_callback = None

        self.read_callback = None
        self.read_encoding = None

        self.write_callback = None
        self.write_encoding = None

        self.ftype = ftype
        self.permissions = permissions

    @property
    def mode(self):
        return self.ftype | self.permissions

    def get(self, *args):
        return self.get_callback(*args)

    def onget(self, callback):
        self.get_callback = callback

    def onread(self, callback, encoding=0o644):
        self.read_callback = callback
        self.read_encoding = encoding

    def onwrite(self, callback, encoding=0o644):
        self.write_callback = callback
        self.write_encoding = encoding

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

            self.file_data.write_callback(data, *self.args)

        return len(data)
