import mafs

import json

fs = mafs.MagicFS()
fs.add_argument('file', help='json file to read from')

# read json file
with open(fs.args.file) as f:
    items = json.load(f)

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
            return { 'st_mode': 0o755 | mafs.FileType.DIRECTORY }
        else:
            return {}

    raise FileNotFoundError()

fs.run()
