class CFG():
    def __init__(self, rules_set, terms_set, nterms_set):
        self.rules = rules_set
        self.terms = terms_set
        self.nterms = nterms_set

    def __repr__(self):
        return '\n'.join(map(str, self.rules))