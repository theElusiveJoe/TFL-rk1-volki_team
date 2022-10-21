from copy import deepcopy

from cfg.rule import Rule, Term, Nterm, Epsilon


class CFG():
    def __init__(self, rules_set, terms_set, nterms_set):
        self.rules = rules_set
        self.terms = terms_set
        self.nterms = nterms_set

        self.buid_dependency_graph()
        self.start = Nterm('[S]')

    def __repr__(self):
        return '\n'.join(map(str, self.rules))

    def buid_dependency_graph(self):
        child_relations = {}
        parent_relations = {}
        for rule in self.rules:
            left = rule.left
            rights = list(filter(lambda x: isinstance(x, Nterm), rule.rights))

            if left not in child_relations:
                child_relations[left] = set(rights)
            else:
                child_relations[left].update(rights)

            for right in rights:
                if right not in parent_relations:
                    parent_relations[right] = set([left])
                else:
                    parent_relations[right].add(left)

        self.child_relations = child_relations
        self.parent_relations = parent_relations

        return self

    def clean(self):
        # убирает нетерминалы:
        # 1. раскрывающиеся только в эпсилон
        # 2. непорождающие
        # 3. недостижимые
        print('cleaning')
        
        self._find_unreachable_symbols()
        self.rules = set(
            filter(lambda x: x.left not in self.unreachable, self.rules))
        self.nterms = self.nterms - self.unreachable

        self._find_nullable_symbols()
        self.rules = set(filter(lambda x: x.left not in self.Ne, self.rules))
        self.rules = set(map(
            lambda x: Rule(x.left, list(
                map(lambda y: y if y not in self.Ne else Epsilon(), x.rights))),
            self.rules
        ))
        
        self.buid_dependency_graph()

    def _find_nullable_symbols(self):
        self.generative = set()

        for rule in self.rules:
            if any(map(lambda x: isinstance(x, Term) and not isinstance(x, Epsilon), rule.rights)):
                self.generative.add(rule.left)

        unallocated = self.nterms.difference(self.generative)

        while True:
            upow = len(unallocated)

            unallocated_copy = deepcopy(unallocated)
            for nterm in unallocated_copy:
                if set(self.child_relations[nterm]) & self.generative:
                    self.generative.add(nterm)
                    unallocated.remove(nterm)

            new_upow = len(unallocated)
            if new_upow == upow:
                break

        self.Ne = unallocated

    def _find_unreachable_symbols(self):
        self.reachable = set([self.start])
        unallocated = self.nterms.difference(self.reachable)

        while True:
            upow = len(unallocated)

            unallocated_copy = deepcopy(unallocated)
            for nterm in unallocated_copy:
                if nterm in self.parent_relations and set(self.parent_relations[nterm]) & self.reachable:
                    self.reachable.add(nterm)
                    unallocated.remove(nterm)

            new_upow = len(unallocated)
            if new_upow == upow:
                break

        self.unreachable = unallocated
