from collections import namedtuple

class Router:
    def __init__(self):
        self.final = None

        self.routes = {}
        self.vroutes = {}

    def add(self, route, data):
        if route:
            if self.final:
                raise RoutingError('candidate node already has value stored')

            try:
                first, rest = route.split('/', 1)
            except ValueError:
                first = route
                rest = None

            if first.startswith(':'):
                first = first[1:]
                if first not in self.vroutes:
                    self.vroutes[first] = Router()
                self.vroutes[first].add(rest, data)
            else:
                if first not in self.routes:
                    self.routes[first] = Router()
                self.routes[first].add(rest, data)
        else:
            if self.routes or self.vroutes:
                raise RoutingError('candidate node already has children')
            else:
                self.final = data

    def lookup(self, route):
        result = self._find(route)
        if result:
            result.data = result.data.final
        return result

    def list(self, route):
        result = self._find(route)
        if result:
            keys = result.data.routes.keys()
            keys = list(keys)
            result.data = keys
        return result

    def _find(self, route):
        if route:
            try:
                first, rest = route.split('/', 1)
            except:
                first = route
                rest = None

            if first in self.routes:
                return self.routes[first]._find(rest)

            for var in self.vroutes:
                result = self.vroutes[var]._find(rest)
                if result:
                    result.parameter(var, first)
                    return result

            return None
        else:
            return Result(self)

class Result:
    def __init__(self, data):
        self.data = data

        self._parameters = {}

    def parameter(self, param, data):
        self._parameters[param] = data

    @property
    def parameters(self):
        Parameters = namedtuple('Parameters', self._parameters.keys())
        return Parameters(**self._parameters)

class RoutingError(Exception):
    pass
