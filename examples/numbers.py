from mafs import MagicFS

fs = MagicFS()


@fs.read('/table')
def numbers(path, ps):
    for i in range(10):
        for j in range(10):
            yield '{:>2} '.format(i * 10 + j)
        yield '\n'


number = 5


@fs.read('/multiple')
def multiple_read(path, ps):
    for i in range(12):
        yield str(number + i * number) + ' '
    yield '\n'


@fs.write('/multiple')
def multiple_write(path, ps):
    def callback(contents):
        global number
        number = int(contents.strip())
    return callback


fs.run()
