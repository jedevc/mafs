# MagicFS (mafs)

MagicFS is an easy-to-use library that allows anyone to easily create virtual
filesystems using FUSE.

MagicFS allows you to redirect file requests, so instead of the request going to
an underlying storage medium like a hard drive, the request goes to a program
that you've written.

If you like the idea of playing around with virtual filesystems, but have been
put off by the complexity of it all, then this library could be for you. You can
easily create whole, feature-complete filesystems in just a few lines of code.
No need for painstakingly dealing with folder structures and buffers, mafs
manages all the low-level details, provides sane defaults, and lets you focus on
the functionality.

## Installation

MagicFS is available on [pypi](https://pypi.org/project/mafs/), and can be
easily installed with pip.

	$ pip3 install mafs

## Examples

All of the examples are listed in `examples/`. Here's a demo of running the
`places.py` example.

	$ mkdir fs
	$ python3 examples/places.py fs
	$ ls fs
	place  shortcut
	$ ls fs/place
	here  there
	$ cat fs/place/here
	this is here
	$ cat fs/place/there
	this is there
	$ cat fs/place/anywhere
	this is anywhere!
	$ fusermount -u fs

## Development

To download MagicFS for development, execute the following commands:

	$ git clone https://github.com/jedevc/mafs.git
	$ cd mafs
	$ pip3 install -r requirements.txt

To launch mafs with an example, execute the following:

	$ PYTHONPATH=. python3 examples/places.py fs -fg

Note the use of the `PYTHONPATH` environment variable to include the
library, and the use of the `-fg` flag to run mafs in the foreground for
easier debugging.

### Tests

To run the tests for MagicFS, install nose, and then use it to run the tests.

	$ pip install nose
	$ nosetests

If you make any changes, please run the tests before you commit to ensure that
you haven't broken anything.
