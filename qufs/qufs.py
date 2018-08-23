import fuse

import argparse

from . import filesystem

class QuickFS:
    def __init__(self):
        self.fs = filesystem.FileSystem()

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('mountpoint', help='folder to mount the filesystem in')
        parser.add_argument('-fg', '--foreground', action='store_true',
                help='run in the foreground')
        args = parser.parse_args()

        self.mount(args.mountpoint, args.foreground)

    def mount(self, mountpoint, foreground=False, threads=False):
        fuse.FUSE(self.fs, mountpoint, raw_fi=True, nothreads=not threads,
                foreground=foreground)

    def onread(self, route, func):
        self.fs.onread(route, func)

    def read(self, route):
        def decorator(func):
            self.onread(route, func)
            return lambda *args, **kwargs: None
        return decorator
