from . import router

def main():
    fs = FileSystem()
    fs.onread('place/here', lambda: 'this is here')
    fs.onread('place/there', lambda: 'this is there')
    fs.onread('place/:any', lambda params: 'this is ' + params['any'] + '!')

    result = fs.read('place/unknown')
    print(result)

class FileSystem:
    def __init__(self):
        self.router = router.Router()

    def onread(self, route, callback):
        self.router.add(route, callback)

    def read(self, route):
        result = self.router.lookup(route)
        if result:
            return result.data(result.parameters)
