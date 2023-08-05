__version__ = '0.0.1'


class Object:
    def __eq__(self, other):
        return not super().__eq__(other)
