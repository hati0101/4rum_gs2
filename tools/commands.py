"""List chat commands: which trigger, which players can type it, and its conditions.

usage: python commands.py <war3map.j> [--mode]   (--mode: only triggers named Mode_*)
"""
import re
import sys
from collections import defaultdict

j = open(sys.argv[1], encoding='utf-8', errors='replace').read()
only_mode = '--mode' in sys.argv
funcs = {m.group(1): m.group(0) for m in re.finditer(r'(?ms)^function (\w+) takes.*?^endfunction', j)}

cmds = defaultdict(lambda: {'players': [], 'exact': set()})
for m in re.finditer(r'TriggerRegisterPlayerChatEvent\( (gg_trg_\w+), ([^,]+(?:\([^)]*\))?), "([^"]*)", (true|false) \)', j):
    trg, who, text, exact = m.groups()
    c = cmds[(trg, text)]
    c['players'].append(who.strip())
    c['exact'].add(exact)

by_trg = defaultdict(list)
for (trg, text), c in cmds.items():
    by_trg[trg].append((text, c))

for trg, lst in sorted(by_trg.items()):
    name = trg[len('gg_trg_'):]
    if only_mode and not name.startswith('Mode'):
        continue
    texts = ', '.join('%r%s' % (t, '' if 'true' in c['exact'] else '(prefix)') for t, c in lst)
    players = sorted(set(p for _, c in lst for p in c['players']))
    print('=' * 70)
    print('%s: %s' % (name, texts))
    print('  players:', ', '.join(players) if len(players) < 6 else '%d registrations' % len(players))
    cond = funcs.get('Trig_%s_Conditions' % name, '')
    for line in cond.splitlines():
        s = line.strip()
        if s.startswith('if ') or s.startswith('return ('):
            print('  cond:', s[:150])
