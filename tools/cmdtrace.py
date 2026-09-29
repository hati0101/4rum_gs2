"""Show which trigger handles a chat command and dump its action/condition code.

usage: python cmdtrace.py <war3map.j> <command> [<command> ...]
"""
import re
import sys

j = open(sys.argv[1], encoding='utf-8', errors='replace').read()
funcs = {m.group(1): m.group(0) for m in re.finditer(r'(?ms)^function (\w+) takes.*?^endfunction', j)}

for cmd in sys.argv[2:]:
    for m in re.finditer(r'TriggerRegisterPlayerChatEvent\( (gg_trg_\w+), [^,]+, "%s", (true|false) \)' % re.escape(cmd), j):
        trg = m.group(1)
        print('=' * 70)
        print('command %r -> %s (exact=%s)' % (cmd, trg, m.group(2)))
        base = trg[len('gg_trg_'):]
        for name, body in funcs.items():
            if name.startswith('Trig_' + base + '_') and not name.startswith('Trig_' + base + '_Func') or name.startswith('Trig_' + base + '_Func'):
                print(body)
        break
