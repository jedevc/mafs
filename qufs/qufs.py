import fuse

from . import filesystem

def main():
    fs = QuickFS()

    @fs.read('/place/here')
    def place_here(ps):
        return 'this is here\n'

    @fs.read('/place/there')
    def place_here(ps):
        return 'this is there\n'

    @fs.read('/place/:any')
    def place_here(ps):
        return 'this is ' + ps['any'] + '!\n'

    fs.mount('test')

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
