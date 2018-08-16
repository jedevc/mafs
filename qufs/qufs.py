import fuse

from . import filesystem

class QuickFS:
    def __init__(self):
        self.fs = filesystem.FileSystem()

    def mount(self, mountpoint):
        fuse.FUSE(self.fs, mountpoint, raw_fi=True, nothreads=True, foreground=True)

    def read(self, route):
        def decorator(func):
            self.fs.onread(route, func)
            def wrapper(*args, **kwargs):
                pass
            return wrapper
        return decorator
