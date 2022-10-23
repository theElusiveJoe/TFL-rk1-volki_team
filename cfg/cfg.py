from copy import deepcopy
import networkx as nx
import uuid


from rule import Rule, Term, Nterm, Epsilon
import uuid


class Mutually_Recursive_Set():
    # https://sites.cs.ucsb.edu/~omer/DOWNLOADABLE/cfg-reg09.pdf
    def __init__(self, members):
        self.members = set(members)


    def add_members(self, members):
        self.members.update(members)

    def can_be_added(self, members):
        return self.members & members

    def __repr__(self):
        return str(self.members)


class CFG():
    def __init__(self, rules_set):
        self.rules = rules_set
        self.terms = self.get_terms(rules_set)
        self.nterms = self.get_nterms(rules_set)
        self.remove_nterms_that_dont_present_at_left()
        # assert all(map(
        #     lambda x: any(map(lambda y: y.left == x, rules_set)),
        #     self.nterms
        # ))
        self.start = Nterm('[S]')
        self.buid_dependency_graph()
        self.clean()

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

    def remove_nterms_that_dont_present_at_left(self):
        presenting_nterms = set()
        new_rules = set()
        for rule in self.rules:
            presenting_nterms.add(rule.left)
        for rule in self.rules:
            new_right = []
            for right in rule.rights:
                if (isinstance(right, Term) or isinstance(right, Nterm) and right in presenting_nterms):
                    new_right.append(right)
            if (len(new_right) == 0):
                new_right.append(Epsilon())
            new_rules.add(Rule(rule.left, new_right))
        self.rules = new_rules
            

    
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
            new_rules.add(Rule(Nterm("[S]"), [Epsilon()]))

        new_rules = new_rules.union(self._gen_all_possible_combinations_of_rules(new_rules))
        return CFG(new_rules)

    def remove_rules_with_only_eps_right(self, rules):
        new_rules = set()
        for rule in rules:
            if (all(map(lambda x: isinstance(x, Epsilon), rule.rights))):
                continue
            new_rules.add(deepcopy(rule))
        return new_rules

    def _gen_all_possible_combinations_of_rules(self, rules):
        combinations = set()
        for rule in rules:
            if any(map(lambda x: x in self.collapsing, rule.rights)):
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

    #нормальна форма Хомского
    def toCNF(self):
        return self.remove_long_rules().remove_epsilon_rules().remove_chain_rules().remove_useless_rules().several_nonterm_removal()


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

    def remove_useless_rules(self):
        return self.remove_nongenerating_rules().remove_unreachable_symbols()

    def remove_nongenerating_rules(self):
        genetaring_nterm = set()
        for rule in self.rules:
            left = rule.left
            rights = rule.rights
            if all(map(lambda x: isinstance(x, Term), rights)):
                genetaring_nterm.add(left.name)
        while True:
            upow = len(genetaring_nterm)
            for rule in self.rules:
                left = rule.left
                rights = rule.rights
                flag = True
                for r in rights:
                    if isinstance(r, Nterm) and not r.name in genetaring_nterm:
                        flag  = False
                        break
                if flag:
                    genetaring_nterm.add(left.name)

            new_upow = len(genetaring_nterm)
            if upow == new_upow:
                break
        new_rules = []
        for rule in self.rules:
            rights = rule.rights
            if any(map(lambda x: isinstance(x, Nterm) and not x.name in genetaring_nterm, rights)):
                continue
            new_rules.append(rule)
        return CFG(new_rules)
    
    def several_nonterm_removal(self):
        def create_unique_str():
            return f"[U{uuid.uuid4().hex[:2].upper()}]" 
        
        rules = set()
        new_rules = []
        to_symbol = {}
        for rule in self.rules:
            left = rule.left
            rights = rule.rights
            if len(rights) == 1 or all(map(lambda x: isinstance(x, Nterm), rights)):
                new_rules.append(rule)
                continue
            rights_new = []
            for r in deepcopy(rights):
                if isinstance(r, Term):
                    if not r.symbol in to_symbol.keys():
                        new_nterm = create_unique_str()
                        to_symbol[r.symbol] = new_nterm
                        new_rules.append(Rule(Nterm(new_nterm), [Term(r.symbol)]))
                        rights_new.append(Nterm(new_nterm))
                    else:
                        rights_new.append(Nterm(to_symbol[r.symbol]))
                else:
                    rights_new.append(r)
            new_rules.append(Rule(left, rights_new))
        return CFG(new_rules)       

    def remove_long_rules(self):
        new_rules = set()
        for rule in self.rules:
            if len(rule.rights) > 2:
                new_rules = new_rules.union(self._split_long_rule(rule))
            else:
                new_rules.add(deepcopy(rule))
        return CFG(new_rules)

    def _split_long_rule(self, rule):
        new_rules = set()
        current_nterm = deepcopy(rule.left)
        new_nterm = Nterm("[U" + uuid.uuid4().hex[:3].upper() + "]")
        for i in range(len(rule.rights) - 2):
            new_rules.add(Rule(current_nterm, [rule.rights[i], new_nterm]))
            current_nterm = new_nterm
            new_nterm = Nterm("[U" + uuid.uuid4().hex[:3].upper() + "]")
        new_rules.add(Rule(current_nterm, [rule.rights[-2], rule.rights[-1]]))
        return new_rules
        
    def clean(self):
        # убирает нетерминалы:
        # 0. ни во что не раскрывающиеся
        # 1. раскрывающиеся только в эпсилон
        # 2. непорождающие
        # 3. недостижимые
        # print('cleaning')

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

    def build_mureses(self):
        # print('-----------------')
        # print('BUILDING MURECES')
        # print('-----------------')
        g = nx.DiGraph(self.child_relations)
        self.cycles = list(nx.simple_cycles(g))
        cycles = list(map(set, self.cycles))
        # for cycle in cycles:
            # print('->cycle', cycle)

        while True:
            cycles = list(filter(bool, cycles))
            cycles_copy = deepcopy(cycles)

            flag_changed = False

            for i, x in enumerate(cycles_copy):
                for j, y in enumerate(cycles_copy):
                    if x == y: 
                        continue
                    if x & y:
                        cycles[i] = x|y
                        cycles[j] = set()
                        flag_changed = True
                        break

            if not flag_changed:
                break
        
        self.mureces = []
        for cycle in cycles:
            self.mureces.append(Mutually_Recursive_Set(cycle))


    def check_murece_on_monocromatic_cycles(self, murece):
        # print('-----------------')
        # print('CHECKING MURACE', murece.members)
        # print('-----------------')
        murece_rules = set(filter(lambda x: x.left in murece.members and set(x.rights) & murece.members, self.rules))
        members = list(murece.members)
        M = [['0' for _ in range(len(members))] for _ in range(len(members))]

        color_l, color_r = False, False
        for i, _ in enumerate(M):
            for j, _ in enumerate(M):
                suitable_rules_for_edge = list(filter(lambda x: x.left == members[i] and members[j] in x.rights, murece_rules)) 
                for sr in suitable_rules_for_edge:
                    if sr.rights[0] == members[j]:
                        color_l = True
                        # if M[i][j] in ['0', 'l']:
                        #      M[i][j] = 'l'
                        # else:
                        #     print('cant color correctly')
                        #     return False

                    if len(sr.rights) > 1 and sr.rights[1] == members[j]:
                        # if M[i][j] in ['0', 'r']:
                        #      M[i][j] = 'r'
                        # else:
                        #     print('cant color correctly')
                        #     return False
                        color_r = True
                    if color_l and color_r:
                        print('cycle is colored badly')
                        return False


        # flatten_matrix = [x for x in list for list in matrix]
        # print('MEMVERS:', members)
        # print('FLATTEN MATRIX', )

        # cycles_base = list(filter(
        #     lambda x: any(map(lambda x: x in murece.members, x)), 
        #     self.cycles))
        # print(self.cycles)
        # print(cycles_base)
        # if len(cycles_base)<=1:
        #     return False


        # color_l, color_r = False, False
        # for cycle in cycles_base:
        #     cycle = cycle.append(cycle[0])
        #     pairs = zip(cycle[:-1], cycle[1])
        #     for pair in pairs:
        #         i = members.index(pair[0])
        #         j = members.index(pair[1])
        #         color_l = color_l or M[i][j] == 'l'
        #         color_r = color_r or M[i][j] == 'r'
        #         if color_l and color_r:
        #             print('cycle is colored badly')
        #             return False
        return True

    def check_task_1(self):
        self.build_mureses()
        # print('MURECES:')
        for murece in self.mureces:
            print(murece.members)
        # print('TRYING TO COLOR MURECES')
        return all(map(lambda x: self.check_murece_on_monocromatic_cycles(x), self.mureces))