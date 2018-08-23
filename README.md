# QuickFS (qufs)

QuickFS is a simple to use tool that allows you to easily create virtual
filesystems using FUSE.

If you've ever wanted to play around with filesystems, but have been put off by
the complexity of libfuse, this library could be for you. You can easily create
whole, feature-complete filesystems in just a few lines of code. No need for
painstakingly dealing with folder structures and buffers, qufs manages all the
low-level details, provides sane defaults, and lets you focus on functionality.

## Installation

	$ git clone https://github.com/jedevc/qufs.git
	$ cd qufs
	$ pip install .

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
