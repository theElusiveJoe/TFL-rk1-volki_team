class Rule():
    def __init__(self, left, rights):
        assert len(rights) > 0
        self.left = left
        self.rights = rights
    
    def __hash__(self):
        return len(str(self.left)) + len(str(self.rights))

    def __eq__(self, o):
        return isinstance(o, Rule) and self.left == o.left and self.rights == self.rights

    def __repr__(self):
        return f'{str(self.left)} -> {"".join(map(str, self.rights))}'

class Term():
    def __init__(self, symbol):
        assert ord('a') <= ord(symbol) <= ord('z') or symbol=='_'
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



class CFG():
    def __init__(self, rules_set, terms_set, nterms_set):
        self.rules = rules_set
        self.terms = terms_set
        self.nterms = nterms_set

    def __repr__(self):
        return '\n'.join(map(str, self.rules))