import re
from cfg import Term, Nterm, Rule, CFG


class CFG_Parser():
    def __init__(self, string):
        self.string = ''.join(filter(lambda x: not str.isspace(x), string))

    def glance(self):
        if self.string == '':
            return ''
        return self.string[0]

    def next(self):
        if self.string == '':
            return -1
        ret = self.string[0]
        self.string = self.string[1:]
        return ret

    def get_nterm(self):
        match = re.match('^\[[A-Z,a-z]+[0-9]*\]', self.string)
        if not match:
            return False

        nterm = match.group(0)
        self.string = self.string[len(nterm):]
        return Nterm(nterm)

    def get_term_or_eps(self):
        if self.glance().isalpha() or self.glance() == '_':
            return Term(self.next())

    def get_arrow(self):
        if self.glance() == '-':
            if self.next() == '-' and self.next() == '>':
                return '->'
            else:
                raise Exception('OBMANKA')

        return False

    def parse_seq(self):
        shtuchki = []
        while self.string:
            shtuchki.append(self.get_nterm())
            shtuchki.append(self.get_term_or_eps())
            shtuchki.append(self.get_arrow())
        return list(filter(bool, shtuchki))


    def parse_rules(self):
        seq = self.parse_seq()
        rules_set = set()
        terms_set = set()
        nterms_set = set()

        rules_raw = []

        arrow_index = -1
        while arrow_index:
            try:
                arrow_index = seq.index('->')
                second_arrow_index = seq.index('->', arrow_index + 1)
            except: 
                rules_raw.append(seq)
                break
            
            rules_raw.append(seq[:second_arrow_index-1])
            seq = seq[second_arrow_index-1:]
        
        for rule_list in rules_raw:
            assert rule_list[1] == '->'
            for tnt in rule_list:
                if isinstance(tnt, Term):
                    terms_set.add(tnt)
                elif isinstance(tnt, Nterm):
                    nterms_set.add(tnt)
            
            new_rule = Rule(rule_list[0], rule_list[2:])
            rules_set.add(new_rule)

        return CFG(rules_set=rules_set, terms_set=terms_set, nterms_set=nterms_set)


if __name__ == '__main__':
    text = '''
        [S] -> [A][T]
        [ERa234] -> a[R95]__db
    '''


    parser = CFG_Parser(text)
    print(parser.parse_rules())