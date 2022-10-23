from copy import deepcopy
from itertools import combinations

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
        for t in terms_set:
            print(t)
        return terms_set

    def get_nterms(self, rules_set):
        nterms_set = set()
        for rule in rules_set:
            rule_list = [rule.left] + rule.rights
            for tnt in rule_list:
                if isinstance(tnt, Nterm):
                    nterms_set.add(tnt)
        for t in nterms_set:
            print(t)
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

    def remove_unreachable_symbols(self):
        new_cfg = deepcopy(self)
        new_cfg._find_unreachable_symbols()
        new_cfg.rules = set(
        filter(lambda x: x.left not in new_cfg.unreachable, new_cfg.rules))
        new_cfg.nterms = new_cfg.nterms - new_cfg.unreachable
        return new_cfg

    def remove_nullable_symbols(self):
        new_cfg = deepcopy(self)
        new_cfg._find_nullable_symbols()
        new_cfg.rules = set(filter(lambda x: x.left not in new_cfg.Ne, new_cfg.rules))
        new_cfg.rules = set(map(
            lambda x: Rule(x.left, list(
                map(lambda y: y if y not in new_cfg.Ne else Epsilon(), x.rights))),
            new_cfg.rules
        ))
        return new_cfg

    def remove_epsilon_rules(self):
        new_rules = deepcopy(self.rules)
        new_rules = self.remove_rules_with_only_eps_right(new_rules)
        self._find_collapsing()
        if (self.start in self.collapsing):
            new_rules.add(Rule(Term("[S]"), [Epsilon()]))

        new_rules = new_rules.union(self._gen_all_possible_combinations_of_rules())
        return CFG(new_rules)

    def remove_rules_with_only_eps_right(self, rules):
        new_rules = set()
        for rule in rules:
            if (len(rule.rights) == 1 and isinstance(rule.rights[0], Epsilon)):
                continue
            new_rules.add(rule)
        return new_rules

    def _gen_all_possible_combinations_of_rules(self):
        combinations = set()
        for rule in self.rules:
            right_comb = self._gen_right_side_combinations(rule.rights, [], 0)
            for comb in right_comb:
                combinations.add(Rule(rule.left, comb))
        return combinations

    def _gen_right_side_combinations(self, right, current_c, current_i):
        if (current_i == len(right)):
            if (all(map(lambda x: isinstance(x, Epsilon), current_c))):
                return []
            return [current_c]
        tmp = []
        if (right[current_i] in self.collapsing):
            tmp += self._gen_right_side_combinations(right, current_c + [Epsilon()], current_i + 1)
        tmp += self._gen_right_side_combinations(right, current_c + [right[current_i]], current_i + 1)
        return tmp


    def _find_collapsing(self):
        self.collapsing = set()
        flag = True
        tmp = deepcopy(self.rules)
        while flag:
            flag = False
            for rule in tmp:
                if (len(rule.rights) == 1 and isinstance(rule.rights[0], Epsilon)):
                    flag = True
                    self.collapsing.add(rule.left)
                    tmp.remove(rule)
                    break
                if all(map(lambda x: isinstance(x, Nterm), rule.rights)) and all(map(lambda x: x in self.collapsing, rule.rights)):
                    self.collapsing.add(rule.left)
                    flag = True
                    tmp.remove(rule)
                    break
        return self


        
    def clean(self):
        # убирает нетерминалы:
        # 0. ни во что не раскрывающиеся
        # 1. раскрывающиеся только в эпсилон
        # 2. непорождающие
        # 3. недостижимые
        print('cleaning')

        return self.remove_unreachable_symbols().remove_nullable_symbols().buid_dependency_graph()

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
