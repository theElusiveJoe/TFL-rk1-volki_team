import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/alex/d/TFL-rk1-volki_team/cfg')

from cfg import CFG
from parser import CFG_Parser


s = '''
[S] -> a[S1]
[X] -> a[Y]
[X] -> b[Y]
[Y] -> a[Y]
[Y] -> b[Y]
[Y] -> cc
[S1]->[X][S2]
[S1]->y[X]
[S1]->y
[S2] -> y[X]
[S2] -> y
'''

a = CFG_Parser(s)
c = a.parse_rules()
ch1 = c.several_nonterm_removal()
print("------------------")
for r in ch1.rules:
    print(r.left.name, r.rights)