from mafs import MagicFS

fs = MagicFS()

@fs.read('/place/here')
def place_here(path, ps):
    return 'this is here\n'

@fs.read('/place/there')
def place_here(path, ps):
    return 'this is there\n'

@fs.read('/place/:any')
def place_here(path, ps):
    return 'this is ' + ps.any + '!\n'

@fs.readlink('/shortcut')
def shortcut(path, ps):
    return './place/a quicker way'

fs.run()
