from copy import deepcopy

from rule import Rule, Term, Nterm, Epsilon


class CFG():
    def __init__(self, rules_set):
        self.rules = rules_set
        self.terms = self.get_terms(rules_set)
        self.nterms = self.get_nterms(rules_set)
        assert all(map(
            lambda x: any(map(lambda y: y.left == x, rules_set)),
            self.nterms
        ))
        self.buid_dependency_graph()
        self.start = Nterm('[S]')

    def get_terms(self, rules_set):
        terms_set = set()
        for rule in rules_set:
            rule_list = [rule.left] + rule.rights
            for tnt in rule_list:
                if isinstance(tnt, Term):
                    terms_set.add(tnt)
        # for t in terms_set:
        #     print(t)
        return terms_set

    def get_nterms(self, rules_set):
        nterms_set = set()
        for rule in rules_set:
            rule_list = [rule.left] + rule.rights
            for tnt in rule_list:
                if isinstance(tnt, Nterm):
                    nterms_set.add(tnt)
        # for t in nterms_set:
        #     print(t)
        return nterms_set

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
    
    def remove_chain_rules(self):
        self._find_chain_rules()
        chainrules = self.ChR

        if len(self.nterms) == len(chainrules):
            return self
        rules = set()
        for rule in self.rules:
            left = rule.left
            rights = rule.rights
            if len(rights) == 1 and type(rights[0]) == Nterm and [left.name, rights[0].name] in chainrules:
                pass
            else:
                rules.add(rule)
        copy_rules = deepcopy(rules)
        for ch in chainrules:
            for rule in copy_rules:
                left = rule.left
                rights = rule.rights
                if ch[1] == left.name:
                    rules.add(Rule(Nterm(ch[0]), rights))
        return CFG(rules)

    def _find_chain_rules(self):
        chainrules = []
        for nterm in self.nterms:
                chainrules.append([nterm.name, nterm.name])
        while True:
            upow = len(chainrules)
            for rule in self.rules:
                left = rule.left
                rights = rule.rights
                if len(rights) == 1 and type(rights[0]) == Nterm:
                    r = rights[0]
                    for ch in chainrules:
                        if ch[1] == left.name:
                            pair  = [ch[0], r.name]
                            if not pair in chainrules:
                                chainrules.append(pair)
            new_upow = len(chainrules)
            if upow == new_upow:
                break
        self.ChR = chainrules

    def clean(self):
        # убирает нетерминалы:
        # 0. ни во что не раскрывающиеся
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

    def is_suitable_for_task_2(self):
        return all(
            map(
                lambda x: len(
                    list(filter(lambda y: isinstance(y, Nterm), x.rights))) <= 1,
                self.rules
            )
        )

    # def find_cycles_in_trs(self):
