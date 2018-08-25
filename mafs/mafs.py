import fuse

import argparse

from . import filesystem

class MagicFS:
    def __init__(self):
        self.fs = filesystem.FileSystem()

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('mountpoint', help='folder to mount the filesystem in')
        parser.add_argument('-fg', '--foreground', action='store_true',
                help='run in the foreground')
        parser.add_argument('-t', '--threads', action='store_true',
                help='use threading')
        args = parser.parse_args()

        self.mount(args.mountpoint, args.foreground, args.threads)

    def mount(self, mountpoint, foreground=False, threads=False):
        fuse.FUSE(self.fs, mountpoint, raw_fi=True, nothreads=not threads,
                foreground=foreground, default_permissions=True)

    # Callbacks
    # =========

    def onread(self, route, func, encoding='utf-8'):
        self.fs.onread(route, func, encoding)

    def onreadlink(self, route, func):
        self.fs.onreadlink(route, func)

    # Callbacks (decorators)
    # ======================

    def read(self, route, encoding='utf-8'):
        def decorator(func):
            self.onread(route, func, encoding)
            return lambda *args, **kwargs: None
        return decorator

    def readlink(self, route):
        def decorator(func):
            self.onreadlink(route, func)
            return lambda *args, **kwargs: None
        return decorator
