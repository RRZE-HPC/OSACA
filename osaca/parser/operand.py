#!/usr/bin/env python3


class Operand:
    def __init__(self, name, source=False, destination=False):
        self._name = name
        self._source = source
        self._destination = destination

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @name.setter
    def name(self, name):
        self._name = name

    @source.setter
    def source(self, source):
        self._source = source

    @destination.setter
    def destination(self, destination):
        self._destination = destination

    def __repr__(self):
        return f"Operand(name={self._name},source={self._source},destination={self._destination})"

    def __str__(self):
        return f"Name: {self._name}, Source: {self._source}, Destination: {self._destination}"
