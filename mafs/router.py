import os

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
        route = os.path.normpath(route)
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
        self.rroutes = {}

    def add(self, route, data):
        if route:
            first, rest = route[0], route[1:]

            if first.startswith(':'):
                first = first[1:]
                if first not in self.vroutes:
                    self.vroutes[first] = Node()
                self.vroutes[first].add(rest, data)
            elif first.startswith('*'):
                first = first[1:]
                if first not in self.rroutes:
                    self.rroutes[first] = Node()
                self.rroutes[first].add(rest, data)
            else:
                if first not in self.routes:
                    self.routes[first] = Node()
                self.routes[first].add(rest, data)
        else:
            if self.final:
                raise RoutingError('node already has assigned value')
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

            for var in self.rroutes:
                vals = []
                while rest:
                    vals.append(first)

                    result = self.rroutes[var].find(rest)
                    if result:
                        result.parameter(var, vals)
                        return result

                    first, rest = rest[0], rest[1:]

                vals.append(first)
                result = Result(self.rroutes[var])
                result.parameter(var, vals)
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
