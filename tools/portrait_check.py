"""Check, against the installed game's files, which portrait model exists for each
hero model the map uses, and how the game's own unitskin.txt fills 'portrait'.

usage: python portrait_check.py "D:\\Warcraft III" <map.w3x>
"""
import re
import sys

from casc import Casc
from objdata import load_units
from w3x import Archive

c = Casc(sys.argv[1])
root = c.root().decode('utf-8', 'replace').splitlines()
files = {}
for line in root:
    parts = line.split('|')
    if len(parts) >= 2 and ':' in parts[0]:
        files[parts[0].lower()] = parts[1]

sd = {k.split(':', 1)[1] for k in files if k.startswith('war3.w3mod:') and not k.startswith('war3.w3mod:_')}
hd = {k.split(':', 1)[1][len('_hd.w3mod:'):] for k in files if k.startswith('war3.w3mod:_hd.w3mod:')}
print('sd files', len(sd), 'hd files', len(hd))

# game's own unitskin.txt: how is 'portrait' written for stock units?
for key in ('war3.w3mod:units/unitskin.txt',):
    if key in files:
        txt = c.read_ckey(bytes.fromhex(files[key])).decode('utf-8', 'replace')
        for uid in ('Hpal', 'Hamg', 'Nsjs', 'Ekee', 'Ofar', 'hfoo'):
            m = re.search(r'^\[%s\]\s*$(.*?)(?=^\[)' % uid, txt, re.M | re.S)
            if m:
                lines = [l for l in m.group(1).splitlines() if re.match(r'(file|portrait|Art)\w*=', l)]
                print(uid, lines)


def norm(p):
    p = p.replace('\\', '/').lower()
    return re.sub(r'\.(mdl|mdx)$', '', p)


arc = Archive(sys.argv[2])
units = load_units(arc)
print('%-5s %-55s %-6s %-6s %s' % ('id', 'model', 'SDpor', 'HDpor', 'model exists sd/hd'))
for uid, u in units.items():
    if not uid[0].isupper() or 'umdl' not in u:
        continue
    m = norm(u['umdl'])
    has = lambda s, x: (x + '.mdx') in s
    print('%-5s %-55s %-6s %-6s %s/%s' % (uid, m, has(sd, m + '_portrait'), has(hd, m + '_portrait'), has(sd, m), has(hd, m)))
