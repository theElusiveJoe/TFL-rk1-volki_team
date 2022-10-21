class Rule():
    def __init__(self, left, rights):
        assert len(rights) > 0
        self.left = left
        if set(rights) == set([Epsilon()]):
            self.rights = [Epsilon()]
        else:
            self.rights = list(filter(lambda x: x != Epsilon(), rights))

    def __hash__(self):
        return len(str(self.left)) + len(str(self.rights))

    def __eq__(self, o):
        return isinstance(o, Rule) and self.left == o.left and self.rights == o.rights

    def __repr__(self):
        return f'{str(self.left)} -> {"".join(map(str, self.rights))}'


class Term():
    def __init__(self, symbol):
        assert ord('a') <= ord(symbol) <= ord('z') 
        self.symbol = symbol

    def __hash__(self):
        return ord(self.symbol)

    def __eq__(self, o):
        return isinstance(o, Term) and self.symbol == o.symbol

    def __repr__(self):
        return self.symbol

    def __str__(self):
        return self.symbol


class Nterm():
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return ord(self.name[-1])

    def __eq__(self, o):
        return isinstance(o, Nterm) and self.name == o.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Epsilon():
    def __init__(self):
        self.symbol = '_'

    def __hash__(self):
        return ord(self.symbol)

    def __eq__(self, o):
        return isinstance(o, Epsilon) and self.symbol == o.symbol

    def __repr__(self):
        return self.symbol

    def __str__(self):
        return self.symbol
