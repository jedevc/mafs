from os import st

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
