import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/alex/d/TFL-rk1-volki_team/cfg')

from cfg import CFG
from parser import CFG_Parser

s = """
[S] -> [A]c
[A] ->[S][D]
[D]->a[D]
[A]->a
"""

a = CFG_Parser(s)
c = a.parse_rules()
ch1 = c.remove_nongenerating_rules()
print("------------------")
for r in ch1.rules:
    print(r.left.name, r.rights)