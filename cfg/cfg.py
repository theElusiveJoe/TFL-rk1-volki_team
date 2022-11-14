from copy import deepcopy
import networkx as nx
import uuid


from cfg.mures2 import Mures
from cfg.rule import Rule, Term, Nterm, Epsilon
from cfg.fa import FA


class Decision(Exception):
    pass


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

        # assert all(map(
        #     lambda x: any(map(lambda y: y.left == x, rules_set)),
        #     self.nterms
        # ))
        self.start = Nterm('[S]')
        self.buid_dependency_graph()
        # self.clean()

    def clean(self):
        # в грамматике не должно быть:
        # 1. недостижимых нетерминалов - unreachable
        # 2. ни во что нераскрывающихся нетерминалов - nonending
        # 3. переходов нетерминал -> нетерминал, которые ничего не выкидывают влево и вправо - chain rules
        # 4. нетерминалов, которые раскрываются только в один конкретный символ
        # 5. правил, правые части которых не epsilon, но там есть "_"
        # 6. правил, правые части которых являются epsilon, но состоят более, чем из одной "_"
        #
        # 3. remove_chain_rules()
        # 2. remove_nongenerating_rules()
        # 4. remove_nonterms_with_single_term_transition()
        # 5. remove_trivial_nterms()
        # 6. remove_trivial_nterms()
        # 1. remove_unreachable_symbols()
        return self.remove_chain_rules() \
            .remove_unreachable_symbols() \
            .remove_nongenerating_rules() \
            .remove_unreachable_symbols() \
            .remove_nonterms_with_single_term_transition()\
            .remove_unreachable_symbols() \
            .remove_trivial_nterms() \
            .remove_unreachable_symbols()

    # извлекает список всех термов из множества правил КСГ
    # используется в конструкторе
    # не изменяет объект
    def get_terms(self, rules_set):
        terms_set = set()
        for rule in rules_set:
            rule_list = [rule.left] + rule.rights
            for tnt in rule_list:
                if isinstance(tnt, Term):
                    terms_set.add(tnt)
        # for t in terms_set:
        #     # print()(t)
        return terms_set

    # извлекает список всех гетермов из множества правил КСГ
    # используется в конструкторе
    # не изменяет объект
    def get_nterms(self, rules_set):
        nterms_set = set()
        for rule in rules_set:
            rule_list = [rule.left] + rule.rights
            for tnt in rule_list:
                if isinstance(tnt, Nterm):
                    nterms_set.add(tnt)
        # for t in nterms_set:
        #     # print()(t)
        return nterms_set

    def __repr__(self):
        return '#################\n' + '#   GRAMMAR:\n#   ' + '\n#   '.join(map(str, self.rules)) + '\n#################'

    # Строит граф зависимостей в КСГ
    # используется в конструкторе
    # не изменяет объект
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

    # Удаляет из списка правил rules все нетерминалы,
    # которых нет ни в одной левой части
    # не меняет объект

    def remove_nterms_that_dont_present_at_left(self, rules):
        presenting_nterms = set()
        new_rules = set()
        for rule in rules:
            presenting_nterms.add(rule.left)
        for rule in rules:
            new_right = []
            for right in rule.rights:
                if (isinstance(right, Term) or isinstance(right, Nterm) and right in presenting_nterms):
                    new_right.append(right)
            if (len(new_right) == 0):
                new_right.append(Epsilon())
            new_rules.add(Rule(rule.left, new_right))
        return new_rules

    # Создает новый объект, в правилах которого удалены недостижимые нетермы
    def remove_unreachable_symbols(self):
        # скажем, что стартовый символ достижим
        self.reachable = set([self.start])
        # про остальные пока не понятно
        unallocated = self.nterms.difference(self.reachable)

        while True:
            upow = len(unallocated)

            unallocated_copy = deepcopy(unallocated)
            for nterm in unallocated_copy:
                # если у трема есть родитель и этот родитель достижим, значит терм достижим
                if nterm in self.parent_relations and set(self.parent_relations[nterm]) & self.reachable:
                    # то пересаживаем его к достижимым
                    self.reachable.add(nterm)
                    unallocated.remove(nterm)

            new_upow = len(unallocated)

            if new_upow == upow:
                break

        new_rules = set(filter(
            lambda x: x.left in reachable,
            self.rules
        ))

        return CFG(new_rules)

    # Удаление eps-правил из грамматики
    # Создает новый объект

    def remove_epsilon_rules(self):
        new_rules = deepcopy(self.rules)
        new_rules = self.remove_rules_with_only_eps_right(new_rules)
        self._find_collapsing()
        if (self.start in self.collapsing):
            new_rules.add(Rule(Nterm("[S]"), [Epsilon()]))

        new_rules = new_rules.union(
            self._gen_all_possible_combinations_of_rules(new_rules))
        new_rules = self.remove_rules_with_only_eps_right(
            self.remove_nterms_that_dont_present_at_left(new_rules))
        if (self.start in self.collapsing):
            new_rules.add(Rule(Nterm("[S]"), [Epsilon()]))
        return CFG(new_rules)

    # Удаляет из списка правил те, у которых в правой части только eps
    # Возвращает новый список, старый не меняет
    # Нужна для удаления eps-правил

    def remove_rules_with_only_eps_right(self, rules):
        new_rules = set()
        for rule in rules:
            if (all(map(lambda x: isinstance(x, Epsilon), rule.rights))):
                continue
            new_rules.add(deepcopy(rule))
        return new_rules

    # Нужна для _gen_all_possible_combinations_of_rules
    # Не меняет объект
    def _gen_right_side_combinations(self, right, current_c, current_i):
        if (current_i == len(right)):
            if (all(map(lambda x: isinstance(x, Epsilon), current_c))):
                return []
            return [current_c]
        tmp = []
        if (right[current_i] in self.collapsing):
            tmp += self._gen_right_side_combinations(
                right, current_c + [Epsilon()], current_i + 1)
        tmp += self._gen_right_side_combinations(
            right, current_c + [right[current_i]], current_i + 1)
        return tmp

    # Генерирует новые правила
    # Нужная для удаления eps-правил
    # Не меняет объект
    def _gen_all_possible_combinations_of_rules(self, rules):
        combinations = set()
        for rule in rules:
            if any(map(lambda x: x in self.collapsing, rule.rights)):
                right_comb = self._gen_right_side_combinations(
                    rule.rights, [], 0)
                for comb in right_comb:
                    combinations.add(Rule(rule.left, comb))
        return combinations

    # Ищет нетермы, которые МОГУТ раскрыться в eps
    # Сохраняет множество таких нетермов в поле объекта collapsing
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

    # Возвращает грамматику в нормальной форме Хомского
    # Возвращает новый объект, старый не меняет
    def toCNF(self):
        # grammar = self.remove_long_rules()
        # print(grammar.terms)
        # grammar = grammar.remove_epsilon_rules()
        # print(grammar.terms)
        # grammar = grammar.remove_chain_rules()
        # print(grammar.terms)

        # grammar = grammar.remove_useless_rules()
        # print(grammar.terms)
        # grammar = grammar.several_nonterm_removal()
        # print(grammar.terms)
        # return grammar

        return self.remove_long_rules() \
            .remove_epsilon_rules() \
            .remove_chain_rules() \
            .remove_useless_rules() \
            .several_nonterm_removal() \

    # Удаляет цепные правила из грамматики
    # Возвращает новый объект

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

    # Возвращает множество цепных правил
    # Нужен remove_chain_rules
    # Сохраняет их в поле объекта ChR
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
                            pair = [ch[0], r.name]
                            if not pair in chainrules:
                                chainrules.append(pair)
            new_upow = len(chainrules)
            if upow == new_upow:
                break
        self.ChR = chainrules

    # Возвращает новый объект без бесполезных правил
    def remove_useless_rules(self):
        return self.remove_nongenerating_rules().remove_unreachable_symbols()

    def remove_nonterms_with_single_term_transition(self):
        useless_nterm = {}
        for nt in self.nterms:
            useless_nterm[nt.name] = None
        for rule in self.rules:
            left = rule.left
            rights = rule.rights
            if len(rights) == 1 and isinstance(rights[0], Term) and left.name in useless_nterm.keys() and useless_nterm[left.name] == None:
                useless_nterm[left.name] = rights[0].symbol
                continue
            useless_nterm.pop(left.name, None)

        new_rules = set()
        for rule in self.rules:
            left = rule.left
            rights = rule.rights
            new_rights = []
            for r in rights:
                if isinstance(r, Nterm) and r.name in useless_nterm.keys():
                    new_rights.append(Term(useless_nterm[r.name]))
                    continue
                new_rights.append(r)
            new_rules.add(Rule(left, new_rights))
        # print()(useless_nterm)
        return CFG(new_rules)

    def remove_nonterms_with_term_transition(self):
        useless_nterm = {}
        unused_nterms = set()
        for nt in self.nterms:
            useless_nterm[nt.name] = None
            unused_nterms.add(nt.name)

        k = 0
        rules = deepcopy(self.rules)
        while True:
            new_rules = set()
            n = k
            for rule in rules:
                left = rule.left
                rights = rule.rights
                if all(map(lambda x: isinstance(x, Term), rights)) and left.name in useless_nterm.keys() and useless_nterm[left.name] == None:
                    useless_nterm[left.name] = rights
                    unused_nterms.remove(left.name)
                    continue
                useless_nterm.pop(left.name, None)

            for rule in rules:
                left = rule.left
                rights = rule.rights
                new_rights = []
                for r in rights:
                    if isinstance(r, Nterm) and r.name in useless_nterm.keys():
                        new_rights.extend(useless_nterm[r.name])
                        n += 1
                        continue
                    new_rights.append(r)
                new_rules.add(Rule(left, new_rights))
            print(n)
            if n == k:
                break
            rules = deepcopy(new_rules)
            k = n
            for nt in self.nterms:
                if nt.name in unused_nterms:
                    useless_nterm[nt.name] = None
                else:
                    useless_nterm.pop(nt.name, None)
        # print()(useless_nterm)
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
                        new_rules.append(
                            Rule(Nterm(new_nterm), [Term(r.symbol)]))
                        rights_new.append(Nterm(new_nterm))
                    else:
                        rights_new.append(Nterm(to_symbol[r.symbol]))
                else:
                    rights_new.append(r)
            new_rules.append(Rule(left, rights_new))
        return CFG(new_rules)

    # Возвращает новый объект, в котором удалены "длинные правила"
    def remove_long_rules(self):
        new_rules = set()
        for rule in self.rules:
            if len(rule.rights) > 2:
                new_rules = new_rules.union(self._split_long_rule(rule))
            else:
                new_rules.add(deepcopy(rule))
        return CFG(new_rules)

    # Возвращает множество правил, в котором "длинные правила" разделены на несколько
    # Нужна для remove_long_rules
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

    def remove_trivial_nterms(self):
        def clean_rules(rules):
            new_rules = set()

            for rule in rules:
                filtered_right_part = list(
                    filter(lambda x: not isinstance(x, Epsilon), rule.rights))
                if filtered_right_part:
                    rule.rights = filtered_right_part
                else:
                    rule.rights = [Epsilon()]
                new_rules.add(rule)
            return new_rules

        rules = clean_rules(self.rules)
        # print()('F CLEANED RULES', rules)
        nterms = self.nterms

        while True:
            nterms_num = len(nterms)

            # на данный момент в каждой правой части стоит не более одного Epsilon()

            for nterm in nterms:
                # найдем все способы его переписывания
                nterms_rules = list(filter(lambda x: x.left == nterm, rules))
                # если он не может переписаться, то это вообще не наш случай
                if not nterms_rules:
                    continue
                # если все способы переписывания тривиальны
                if all(map(lambda x: x.rights == [Epsilon()], nterms_rules)):
                    # print()('TRIVIAL FOUND', nterm, nterms_rules)

                    # обновим правила
                    rewrittent_rules = set()
                    for rule in rules:
                        rule.rights = list(
                            map(lambda x: x if x != nterm else Epsilon(), rule.rights))
                        rewrittent_rules.add(rule)
                        # print()('FILTERED RULE', rule)
                    rules = rewrittent_rules

                    nterms.remove(nterm)
                    rules = list(filter(lambda x: nterm != x.left, rules))
                    break

            rules = clean_rules(rules)
            # print()('CLEANED RULES', rules)

            if len(nterms) == nterms_num:
                break

        return CFG(rules)

    # Возвращает новый объект, в котором удалены nonegenerating правила
    # (nongenerating - непораждающие. Для них в правой части всегда стоит хотя бы один нетерминал)
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
                        flag = False
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

    def remove_unreachable_symbols(self):
        # скажем, что стартовый символ достижим
        self.reachable = set([self.start])
        # про остальные пока не понятно
        unallocated = self.nterms.difference(self.reachable)

        while True:
            upow = len(unallocated)

            unallocated_copy = deepcopy(unallocated)
            for nterm in unallocated_copy:
                # если у трема есть родитель и этот родитель достижим, значит терм достижим
                if nterm in self.parent_relations and set(self.parent_relations[nterm]) & self.reachable:
                    # то пересаживаем его к достижимым
                    self.reachable.add(nterm)
                    unallocated.remove(nterm)

            new_upow = len(unallocated)

            if new_upow == upow:
                break

        new_rules = set(filter(
            lambda x: x.left in self.reachable,
            self.rules
        ))

        return CFG(new_rules)

    def build_mureses(self):
        # # print()('-----------------')
        # # print()('BUILDING muresES')
        # # print()('-----------------')
        g = nx.DiGraph(self.child_relations)
        self.cycles = list(nx.simple_cycles(g))
        cycles = list(map(set, self.cycles))
        # for cycle in cycles:
        # # print()('->cycle', cycle)

        while True:
            cycles = list(filter(bool, cycles))
            cycles_copy = deepcopy(cycles)

            flag_changed = False

            for i, x in enumerate(cycles_copy):
                for j, y in enumerate(cycles_copy):
                    if x == y:
                        continue
                    if x & y:
                        cycles[i] = x | y
                        cycles[j] = set()
                        flag_changed = True
                        break

            if not flag_changed:
                break

        self.mureses = []
        for cycle in cycles:
            self.mureses.append(Mutually_Recursive_Set(cycle))

    # ЗАДАНИЕ 1

    def check_task_1(self):

        self.build_mureses()
        # # print()('muresES:')
        # for murese in self.mureses:
        # print()(murese.members)
        # # print()('TRYING TO COLOR muresES')
        return all(map(lambda x: self.check_murese_on_monocromatic_cycles(x), self.mureses))

    def check_murese_on_monocromatic_cycles(self, murese):
        # # print()('-----------------')
        # # print()('CHECKING muresE', murese.members)
        # # print()('-----------------')
        murese_rules = set(filter(lambda x: x.left in murese.members and set(
            x.rights) & murese.members, self.rules))
        members = list(murese.members)
        M = [['0' for _ in range(len(members))] for _ in range(len(members))]

        color_l, color_r = False, False
        for i, _ in enumerate(M):
            for j, _ in enumerate(M):
                suitable_rules_for_edge = list(
                    filter(lambda x: x.left == members[i] and members[j] in x.rights, murese_rules))
                for sr in suitable_rules_for_edge:
                    if sr.rights[0] == members[j]:
                        color_l = True

                    if len(sr.rights) > 1 and sr.rights[1] == members[j]:
                        color_r = True
                    if color_l and color_r:
                        print('cycle is colored badly')
                        return False

        # flatten_matrix = [x for x in list for list in matrix]
        # # print()('MEMVERS:', members)
        # # print()('FLATTEN MATRIX', )

        # cycles_base = list(filter(
        #     lambda x: any(map(lambda x: x in murese.members, x)),
        #     self.cycles))
        # # print()(self.cycles)
        # # print()(cycles_base)
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
        #             # print()('cycle is colored badly')
        #             return False
        return True

    # ЗАДАНИЕ 2

    def check_task_2(self):
        # ограничения метода
        # 1. считаем, что все правила в правой части имеют не более одного нетерминала
        # 2. если в исходной грамматике 1. не соблюден, то до применения метода все незацикленные нетерминалы должны развернуться в терминалы
        # 3. из любого muresa не более одного выхода
        self.build_mureses()
        print(self)
        print(self.mureses)
        try:
            return self.check_linear_split(self.start)
        except AssertionError:
            return False
        except Decision:
            return True
        return False

    def check_linear_split(self, first_cycled_nterm):
        # print()('----------------------------------')
        # print()('CHECKING LINEAR SPLIT OF', first_cycled_nterm)

        # 1 МЫ НЕ В MURESE НАХОДИМСЯ СЕЙЧАС
        if not any(map(lambda x: first_cycled_nterm in x.members, self.mureses)):
            # правила, по которым можно отсюда уйти (и, кстати, в этом проходе в глубину мы сюда уже не вернемся)
            transit_rules = list(
                filter(lambda x: first_cycled_nterm == x.left, self.rules))

            # предполагаем, что тут нет ветвлений грамматики
            assert len(transit_rules) == 1
            # выцепили правило перехода
            return self.transit_to_next_node(transit_rules[0])

        # 2 МЫ В MURESE НАХОДИМСЯ СЕЙЧАС
        # print()('WE REACHED MURESE', first_cycled_nterm)
        cycles = list(filter(lambda x: first_cycled_nterm in x, self.cycles))
        # НАМ ОЧЕНЬ ХОЧЕЦА, ЧТОБЫ ЦИКЛ БЫЛ ОДИН ЭТОТ ЦИКЛ
        assert len(cycles) == 1
        the_cycle = cycles[0]

        # сейчас пройдемся по этому циклу и посмотрим, что прилипнет к бортам нашего судна
        i = the_cycle.index(first_cycled_nterm)
        the_cycle = the_cycle[i:] + the_cycle[:i]
        the_cycle.append(the_cycle[0])
        left_tumor, right_tumor = [], []
        for i in range(len(the_cycle)-1):
            # вот правила, по которым мы можем двигаться по циклу дальше
            rules = list(filter(
                lambda x: the_cycle[i] == x.left and the_cycle[i+1] in x.rights, self.rules))
            # ну и тут тоже пока что надеемся
            # возможно, этот ассерт лишний вообще, но пусть будет
            assert len(rules) == 1
            rule = rules[0]
            pos_in_rule = rule.rights.index(the_cycle[i+1])
            left_tumor, right_tumor = left_tumor + \
                rule.rights[:pos_in_rule], right_tumor + \
                rule.rights[pos_in_rule+1:]

        # print()('TUMORS', left_tumor, right_tumor)

        # получим выходы из этого Mures'а
        escape_rules = list(filter(lambda x: x.left in the_cycle and all(
            map(lambda y: y not in the_cycle, x.rights)), self.rules))
        # print()('ESCAPE RULES', escape_rules)

        assert len(escape_rules) == 1
        mid_string = self.transit_to_next_node(escape_rules[0])
        # print()('MID', mid_string)

        # мы хотим, чтобы нарастали только буковки!!
        assert all(map(lambda x: isinstance(x, Term), left_tumor)) and all(map(lambda x: isinstance(x, Term), right_tumor))\

        left_string = ''.join(map(str, left_tumor))
        right_string = ''.join(map(str, right_tumor))

        # ну а тут перебором ищем линейное разделение
        for i in range(0, len(left_string)):
            for j in range(len(mid_string)):
                if left_string[len(left_string) - i:] + mid_string[:j] not in mid_string+right_string:
                    # print('suitable for task 2: IRREGULAR')
                    raise Decision()

        for i in range(0, len(right_string)):
            for j in range(len(mid_string)):
                if mid_string[len(mid_string) - j:] + right_string[:i] not in left_string+mid_string:
                    # print('suitable for task 2: IRREGULAR')
                    raise Decision()

        return mid_string

    def transit_to_next_node(self, rule):
        # по правилу мы должны куда-то переместиться
        # убедимся, что справа максимум один нетерминал
        # вернем то, что нарастетслева и справа при переходе + минимум того, что раскроется в середине
        # print('TRANSITTING', rule)
        assert (len(list(filter(lambda x: isinstance(x, Nterm), rule.rights)))) <= 1
        rights = rule.rights
        i = 0
        # попробуем найти этот нетерминал
        while i < len(rights):
            if isinstance(rights[i], Nterm):
                # нашли этот нетерминал, значит прогуляемся по нему
                mid_string = self.check_linear_split(rights[i])
                return ''.join(map(str, rights[:i])) + mid_string + ''.join(map(str, rights[i+1:]))
            i += 1
        else:
            # если это конечный узел, возвращаем его термы
            return ''.join(map(str, rights))

    # ЛАБА 3

    def check_lab_3(self):
        # предварительная подготовка
        self.prepare_to_lab_3()

        print('\nВИДЫ НТЕРМОВ В ГРАММАТИКЕ:')
        print('циклические:', self.nodes_in_mureses)
        print('транзитные:', self.transit_nodes)
        print('конечные:', self.finite_nodes)

        # проверим, что подходит под наши ограничения
        if not self.is_suitable_for_lab_3():
            return False

        return True
        # for m in self.mureses2:
        #     print()
        #     print(m)
        #     m.check_idempotence()


    def prepare_to_lab_3(self):
        def get_nodes_in_mureses(self):
            g = nx.DiGraph(self.child_relations)
            cycles = nx.simple_cycles(g)
            nodes_in_mureses = set()
            for cycle in cycles:
                nodes_in_mureses.update(cycle)
            return nodes_in_mureses

        def get_transit_nodes(self):
            transit_nodes = set()
            while True:
                for node in self.nterms:
                    if node in self.nodes_in_mureses or node in transit_nodes:
                        continue
                    if any(map(lambda x: x in transit_nodes or x in self.nodes_in_mureses, self.child_relations[node])):
                        transit_nodes.add(node)
                        break
                else:
                    break
            return transit_nodes

        def get_finite_nodes(self):
            return self.nterms - (self.transit_nodes | self.nodes_in_mureses)

        # все ноды разделим на 3 множества
        self.nodes_in_mureses = get_nodes_in_mureses(self)
        self.transit_nodes = get_transit_nodes(self)
        self.finite_nodes = get_finite_nodes(self)

        #  построим мюресы
        self.build_mureses_2()

    def build_mureses_2(self):
        g = nx.DiGraph(self.child_relations)
        cycles = list(map(set, nx.simple_cycles(g)))

        while True:
            cycles = list(filter(bool, cycles))
            cycles_copy = deepcopy(cycles)

            for i, x in enumerate(cycles_copy):
                for j, y in enumerate(cycles_copy):
                    if x == y:
                        continue
                    if x & y:
                        cycles[i] = x | y
                        cycles[j] = set()
                        break
            else:
                break

        self.mureses2 = set()
        for cycle in cycles:
            self.mureses2.add(Mures(self, cycle))

    def find_mures_by_node(self, node):
        return list(filter(lambda x: node in x, self.mureses2))[0]

    def is_suitable_for_lab_3(self):
        for rule in self.rules:
            if rule.left not in self.nodes_in_mureses:
                continue
            if len(rule.rights) == 1:
                continue

            the_mures = self.find_mures_by_node(rule.left)

            a, b = rule.rights
            if (a in the_mures and b not in self.finite_nodes) or (b in the_mures and a not in self.finite_nodes):
                return False

        return True

    def build_fa_for_appendix(self, node):
        assert node in self.finite_nodes
        trs_rules = list(filter(lambda x: x.left == node, self.rules))

        fa = FA()

        for rule in trs_rules:
            if len(rule.rights) == 1:
                fa.add_transit(
                    fa.start_node, fa.finish_node, rule.rights[0].symbol
                )
            else:
                fa1 = self.build_fa_for_appendix(rule.rights[0])
                fa2 = self.build_fa_for_appendix(rule.rights[1])
                fa_sum = fa1.concat(fa2)
                fa.insert(fa_sum)

        return fa

    # def build_regular_approximation(self, node=None):
    #     if not node:
    #         return self.build_regular_approximation(self.start)

    #     if node in self.nodes_in_mureses:
    #         the_mures = self.find_mures_by_node(node)
    #         return
