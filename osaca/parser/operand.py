#!/usr/bin/env python3


class Operand:
    def __init__(self, source=False, destination=False):
        self._source = source
        self._destination = destination

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @source.setter
    def source(self, source):
        self._source = source

    @destination.setter
    def destination(self, destination):
        self._destination = destination

    def __str__(self):
        return f"Operand(Source: {self._source}, Destination: {self._destination})"

    def __repr__(self):
        return self.__str__()
