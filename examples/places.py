from mafs import MagicFS

fs = MagicFS()

@fs.readall('/place/here')
def place_here(path, ps):
    return 'this is here\n'

@fs.readall('/place/there')
def place_here(path, ps):
    return 'this is there\n'

@fs.readall('/place/:any')
def place_here(path, ps):
    return 'this is ' + ps.any + '!\n'

@fs.readlink('/shortcut')
def shortcut(path, ps):
    return './place/a quicker way'

fs.run()
