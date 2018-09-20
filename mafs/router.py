from collections import namedtuple

class Router:
    def __init__(self):
        self.root = Node()

    def add(self, route, data):
        route = self._split_route(route)

        self.root.add(route, data)

    def lookup(self, route):
        route = self._split_route(route)

        result = self.root.find(route)
        if result:
            result.data = result.data.final
        return result

    def list(self, route):
        route = self._split_route(route)

        result = self.root.find(route)
        if result:
            keys = result.data.routes.keys()
            keys = list(keys)
            result.data = keys
        return result

    def _split_route(self, route):
        if route == '/':
            return []
        else:
            route = route.strip('/')
            return route.split('/')

class Node:
    def __init__(self):
        self.final = None

        self.routes = {}
        self.vroutes = {}

    def add(self, route, data):
        if route:
            if self.final:
                raise RoutingError('candidate node already has value stored')

            first, rest = route[0], route[1:]

            if first.startswith(':'):
                first = first[1:]
                if first not in self.vroutes:
                    self.vroutes[first] = Node()
                self.vroutes[first].add(rest, data)
            else:
                if first not in self.routes:
                    self.routes[first] = Node()
                self.routes[first].add(rest, data)
        else:
            if self.routes or self.vroutes:
                raise RoutingError('candidate node already has children')
            else:
                self.final = data

    def find(self, route):
        if route:
            first, rest = route[0], route[1:]

            if first in self.routes:
                result = self.routes[first].find(rest)
                if result:
                    return result

            for var in self.vroutes:
                result = self.vroutes[var].find(rest)
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
