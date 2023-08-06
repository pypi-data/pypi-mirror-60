import re


class Attribute:
    regex = re.compile(r'^$')

    def __init__(self, filter_func=lambda line: line, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.open = True
        self.value_ = None
        self.filter = filter_func

    def name(self):
        '''
        Return the name of the attribute.

        Returns
        -------
        result: string
            name (It equals class name is the default.)

        UnitTesting
        -------
        >>> Attribute().name()
        'Attribute'
        '''
        return type(self).__name__

    def value(self):
        '''
        >>> Attribute().value()
        '''
        return self.value_

    def is_open(self):
        '''
        >>> Attribute().is_open()
        True
        '''
        return self.open

    def is_empty(self):
        '''
        >>> Attribute().is_empty()
        True
        '''
        return self.value_ == None

    def test(self, line):
        match = self.regex.search(line)
        return match != None

    def set(self, line):
        return self


if __name__ == '__main__':
    import doctest
    doctest.testmod()
