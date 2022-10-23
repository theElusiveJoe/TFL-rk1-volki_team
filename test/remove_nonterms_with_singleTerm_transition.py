import sys
sys.path.insert(1, '/home/alex/d/TFL-rk1-volki_team/cfg')

from cfg import CFG
from parser import CFG_Parser

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
[S2] -> y
'''

s = """
[S] -> [T]x
[T] -> [S1][S2]
[S1]->[S2]
[S2] -> y
[X] -> ab
"""

a = CFG_Parser(s)
c = a.parse_rules()
c = c.remove_chain_rules().remove_unreachable_symbols()

print("---------------")
for i in c.rules:
    print(i.left, i.rights)
c = c.remove_nonterms_with_singleTerm_transition()
print("--------------")
for i in c.rules:
    print(i.left, i.rights)