from qufs import QuickFS

fs = QuickFS()

@fs.read('/place/here')
def place_here(ps):
    return 'this is here\n'

@fs.read('/place/there')
def place_here(ps):
    return 'this is there\n'

@fs.read('/place/:any')
def place_here(ps):
    return 'this is ' + ps['any'] + '!\n'

fs.run()
