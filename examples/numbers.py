from mafs import MagicFS

fs = MagicFS()

@fs.read('/table')
def numbers(path, ps):
    for i in range(10):
        for j in range(10):
            yield '{:>2} '.format(i * 10 + j)
        yield '\n'

fs.run()
