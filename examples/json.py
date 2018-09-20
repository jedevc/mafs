import mafs
import stat

fs = mafs.MagicFS()

items = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': {
        'e': 4,
        'f': 5
    }
}

def dig(d, parts):
    if parts:
        try:
            res = d.get(parts[0])
            if res:
                return dig(res, parts[1:])
        except (KeyError, AttributeError):
            return None
    else:
        return d

@fs.read('/*item')
def read_item(path, ps):
    return str(dig(items, ps.item)) + '\n'

@fs.list('/')
def list_root(path, ps):
    return items.keys()

@fs.list('/*item')
def list_item(path, ps):
    return dig(items, ps.item).keys()

@fs.stat('/*item')
def stat_item(path, ps):
    item = dig(items, ps.item)

    if item:
        if hasattr(item, 'get'):
            return { 'st_mode': 0o755 | stat.S_IFDIR }
        else:
            return {}

    raise mafs.FileNotFoundError()

fs.run()
