# MagicFS (mafs)

MagicFS is a simple-to-use tool that allows you to easily create virtual
filesystems using FUSE.

If you've ever wanted to play around with filesystems, but have been put off by
the complexity of libfuse, this library could be for you. You can easily create
whole, feature-complete filesystems in just a few lines of code. No need for
painstakingly dealing with folder structures and buffers, mafs manages all the
low-level details, provides sane defaults, and lets you focus on functionality.

## Installation

MagicFS is available on pypi, and is easily installable with pip.

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
