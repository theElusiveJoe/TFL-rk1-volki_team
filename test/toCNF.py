import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/alex/d/TFL-rk1-volki_team/cfg')

from cfg import CFG
from parser import CFG_Parser


s = """
[S]->a[X]y[X]
[S]->a[Z] 
[X]->a[Y]
[X]->b[Y]
[X]->_
[Y]->[X]
[Y]->cc
[Z]->[Z][X]
"""

s2 = '''
[S] -> a[S1]
[S] -> a[Z]
[X] -> a[Y]
[X] -> b[Y]
[Y] -> a[Y]
[Y] -> b[Y]
[Y] -> cc
[Z] -> [Z][X]
[S1]->[X][S2]
[S1]->[S2]
[S2] -> y[X]
[S2] -> y
'''

a = CFG_Parser(s)
c = a.parse_rules()
cnf = c.remove_long_rules()
cnf = cnf.remove_epsilon_rules()


a2 = CFG_Parser(s2)
c2 = a2.parse_rules()
cnf = c2.remove_chain_rules().remove_nullable_symbols()

s3 = """
[S] -> [A]c
[A] -> [S][D]
[D] -> a[D]
[A] -> a
"""
a3 = CFG_Parser(s2)
c3 = a3.parse_rules()
print(len(c3.rules))
for i in c3.rules:
    print(i.left, i.rights)
c3 = c3.remove_chain_rules().remove_useless_rules().several_nonterm_removal()
# c3 = c3.remove_useless_rules()
print("--------------")
print(len(c3.rules))
for i in c3.rules:
    print(i.left, i.rights)