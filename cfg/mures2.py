from cfg.rule import *
from cfg.fa import FA
from cfg.tools import *
from random import choice


class Mures:
    def __init__(self, grammar, members):
        self.members = members
        self.grammar = grammar
        self.internal_rules = list(filter(
            lambda r:
                r.left in members
                and
                len(list(filter(lambda x: x in members, r.rights))) == 1,
            grammar.rules))
        self.escape_rules = list(filter(
            lambda r:
                r.left in members
                and
                len(list(filter(lambda x: x in members, r.rights))) == 0,
            grammar.rules))

    def __repr__(self):
        nl = '\n'
        # members = f'members: {" ".join(map(str, self.members))}'
        # internal_rules = f'rules:{nl}{nl.join(map(str, self.internal_rules))}'
        # escape_rules = f'escapes:{nl}{nl.join(map(str, self.escape_rules))}'
        return (
            '#'*10
            + nl
            + nl.join(map(
                lambda x: '#   ' + str(x),
                [
                    'MURES2',
                    'members:', self.members,
                    'rules:', *list(map(lambda x: '    ' +
                                    str(x), self.internal_rules)),
                    'escapes:', *list(map(lambda x: '    ' +
                                          str(x), self.escape_rules))
                ]))
            + nl
            + '#'*10
        )

    def __contains__(self, o):
        return o in self.members or o in self.internal_rules or o in self.escape_rules

    def check_idempotence(self):

        self.left_rules = set()
        self.right_rules = set()
        for rule in self.internal_rules:
            a, b = rule.rights
            if a in self.members:
                self.right_rules.add(rule)
                self.left_rules.add(Rule(rule.left, [a]))
            else:
                self.left_rules.add(rule)
                self.right_rules.add(Rule(rule.left, [b]))

        print('нарастает слева:', self.left_rules)
        print('нарастает справа;', self.right_rules)

        left_fa = self.build_left_fa(list(self.members)[0])
        print(left_fa)
        right_fa = self.build_right_fa(list(self.members)[0])
        print(right_fa)

        # left_fa.to_dot('many_graphs.dot')
        right_fa.to_dot('many_graphs.dot')


    def build_left_fa(self, with_respect_node:str):
        print('\n\nBUILDING LEFT FA:')
        with_respect_node = str(with_respect_node)
        fa = FA()
        fa.add_nodes(self.members)

        fa.add_transit(fa.start_node, with_respect_node, '')

        for rule in self.left_rules:
            if len(rule.rights) == 1:
                fa.add_transit(
                    rule.left.name,
                    rule.rights[0].name if rule.rights[0].name != with_respect_node else fa.finish_node,
                    '')
            else:
                appendix_fa = self.grammar.build_fa_for_appendix(
                    rule.rights[0].name)
                fa.insert(
                    appendix_fa,
                    insert_start=rule.left.name,
                    insert_end=rule.rights[1]
                )

        return fa

    def build_right_fa(self, with_respect_node:str):
        print('\n\nBUILDING RIGHT FA:')
        with_respect_node = str(with_respect_node)
        fa = FA()
        fa.add_nodes(self.members)

        fa.add_transit(fa.start_node, with_respect_node, '')

        for rule in self.right_rules:
            if len(rule.rights) == 1:
                fa.add_transit(
                    rule.rights[0].name ,
                    rule.left.name if rule.left.name != with_respect_node else fa.finish_node,
                    '')
            else:
                appendix_fa = self.grammar.build_fa_for_appendix(
                    rule.rights[1].name)
                fa.insert(
                    appendix_fa,
                    insert_end=rule.left.name if rule.left.name!=with_respect_node else fa.finish_node,
                    insert_start=rule.rights[0]
                )

        return fa
