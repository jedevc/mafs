import fuse
import stat
import errno

import argparse

from . import filesystem

class MagicFS:
    '''
    The main class for building magic filesystems.

    Each of the callbacks takes a route and a function to call for paths that
    match that route. Some callbacks (such as read or write) also optionally
    take an encoding; this is used to encode or decode strings that are
    accepted or returned from callbacks. If the encoding=None, then the string
    is assumed to be a byte-string.

    Routes
    ======
    A route takes the form of a path, e.g. /foo/bar which only matches the
    path /foo/bar. It can also contain variables, which have a colon prefixed,
    e.g. /foo/:var which matches any file in the directory /foo. Finally, it
    can contain recursive variables which match at least one directory, e.g.
    /foo/*var, which matches any file in /foo, such as /foo/bar or /foo/bar/baz.

    Callbacks
    =========
    Functions provided as callbacks should return different data types depending
    on what kind of action they perform. For specific details, see the
    documentatation for each callback register.
    '''

    def __init__(self):
        self.fs = filesystem.FileSystem()

        self._user_args = []
        self._args = None

    def mount(self, mountpoint, foreground=False, threads=False):
        '''
        Mount the filesystem.
        '''

        fuse.FUSE(self.fs, mountpoint, raw_fi=True, nothreads=not threads,
                foreground=foreground, default_permissions=True)

    def run(self):
        '''
        Mount the filesystem using options provided at the command line.
        '''

        args = self.args
        self.mount(args.mountpoint, args.foreground, args.threads)

    def add_argument(self, *args, **kwargs):
        '''
        Add command line arguments for the run() method.

        Each argument is not operated on now, but stored to be added later.
        '''

        self._user_args.append((args, kwargs))

    @property
    def args(self):
        if not self._args:
            parser = argparse.ArgumentParser()
            parser.add_argument('mountpoint',
                    help='folder to mount the filesystem in')
            parser.add_argument('-fg', '--foreground', action='store_true',
                    help='run in the foreground')
            parser.add_argument('-t', '--threads', action='store_true',
                    help='allow the use of threads')

            for (args, kwargs) in self._user_args:
                parser.add_argument(*args, **kwargs)

            self._args = parser.parse_args()

        return self._args

    # Callbacks
    # =========

    def onread(self, route, func, encoding='utf-8'):
        '''
        Register a callback for read requests.

        The callback can return:
            - None
            - a string
            - an iterable (or generator)
            - a readable file object
            - a function taking two parameters, length and offset, and returning
              a byte string
        '''

        self.fs.onread(route, func, encoding)

    def onwrite(self, route, func, encoding):
        '''
        Register a callback for write requests.

        The callback can return:
            - None
            - a writable file object
            - a function taking one parameter, the string to write
            - a function taking two parameters, a byte string and offset
        '''

        self.fs.onwrite(route, func, encoding)

    def onlist(self, route, func):
        '''
        Register a callback for listdir requests.

        The callback can return:
            - an iterable (or generator)
        '''

        self.fs.onlist(route, func)

    def onstat(self, route, func):
        '''
        Register a callback for file stat requests.

        The callback can return:
            - None
            - a dictionary containing any of:
                - 'st_atime', 'st_ctime', 'st_mtime'
                - 'st_gid', 'st_uid'
                - 'st_mode'
                - 'st_nlink'
                - 'st_size'

        Note that for 'st_mode', you should use the bitwise 'or' to combine the
        file type and the file permissions, e.g. FileType.REGULAR | 0o644.

        If the callback throws a FileNotFoundException, it will be interpreted
        as a sign that the indicated file does not exist.
        '''

        self.fs.onstat(route, func)

    def onreadlink(self, route, func):
        '''
        Register a callback for readlink requests.

        The callback can return:
            - a string pathname
        '''

        self.fs.onreadlink(route, func)

    # Callbacks (decorators)
    # ======================

    def file(self, route, encoding='utf-8'):
        '''
        Register various callbacks using a class decorator.

        The read and write methods of the class are added as their respective
        callback types.
        '''

        def decorator(cls):
            if hasattr(cls, 'read'):
                self.onread(route, cls.read, encoding)
            if hasattr(cls, 'write'):
                self.onwrite(route, cls.write, encoding)

            return cls
        return decorator

    def read(self, route, encoding='utf-8'):
        '''
        Register a callback for read requests using a function decorator.

        See onread().
        '''

        def decorator(func):
            self.onread(route, func, encoding)
            return func
        return decorator

    def write(self, route, encoding='utf-8'):
        '''
        Register a callback for write requests using a function decorator.

        See onwrite().
        '''

        def decorator(func):
            self.onwrite(route, func, encoding)
            return func
        return decorator

    def list(self, route):
        '''
        Register a callback for listdir requests using a function decorator.

        See onlist().
        '''

        def decorator(func):
            self.onlist(route, func)
            return func
        return decorator

    def stat(self, route):
        '''
        Register a callback for stat requests using a function decorator.

        See onstat().
        '''

        def decorator(func):
            self.onstat(route, func)
            return func
        return decorator

    def readlink(self, route):
        '''
        Register a callback for readlink requests using a function decorator.

        See onreadlink().
        '''

        def decorator(func):
            self.onreadlink(route, func)
            return func
        return decorator

class FileType:
    '''
    Helper variables for calculating permissions.
    '''

    REGULAR = stat.S_IFREG

    DIRECTORY = stat.S_IFDIR
    FOLDER = stat.S_IFDIR

    LINK = stat.S_IFLNK
