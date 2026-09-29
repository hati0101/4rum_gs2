"""Hero skill slots (Q/W/E/R) and passive detection for the team panel.

For each hero-type unit: hero abilities (uhab) are placed by the hotkey written
in their learn/tooltip text, e.g. "파워 스트라이크 배우기(Q)". An ability is
treated as passive when its cooldown is 0 on every level (unset fields use the
game's stock value from abilitydata.slk when the game is available).

usage: python skills.py <map.w3x> [--game "D:\\Warcraft III"]
"""
import re
import sys

from objdata import load_objects, load_strings, load_units, resolve
from w3x import Archive

SLOTS = 'QWER'
STAT_BONUS = 'A04T'


def stock_cooldowns(game_dir):
    """{base ability id: [Cool1..Cool4]} from the installed game's abilitydata.slk."""
    from casc import Casc
    c = Casc(game_dir)
    key = None
    for line in c.root().decode('utf-8', 'replace').splitlines():
        if line.lower().startswith('war3.w3mod:units/abilitydata.slk|'):
            key = line.split('|')[1]
    rows, cur = {}, None
    for ln in c.read_ckey(bytes.fromhex(key)).decode('utf-8', 'replace').splitlines():
        if ln.startswith('C;'):
            parts = dict((x[0], x[1:]) for x in ln.split(';')[1:] if x)
            if 'Y' in parts:
                cur = int(parts['Y'])
            rows.setdefault(cur, {})[int(parts['X'])] = parts.get('K', '').strip('"')
    hdr = {v: k for k, v in rows[1].items()}
    out = {}
    for y, r in rows.items():
        code = r.get(hdr['code'])
        if code:
            vals = []
            for lv in range(1, 5):
                try:
                    vals.append(float(r.get(hdr.get('Cool%d' % lv), '0') or 0))
                except ValueError:
                    vals.append(0.0)
            out[code] = vals
    return out


def skill_table(arc, game_dir=None):
    """{unit id: [(slot, ability id, passive)]} ordered Q, W, E, R."""
    strings = load_strings(arc)
    units = load_units(arc)
    abil = load_objects(arc, 'war3map.w3a')
    skin = load_objects(arc, 'war3mapSkin.w3a')
    stock = stock_cooldowns(game_dir) if game_dir else {}

    def text(aid):
        s = skin.get(aid, {})
        parts = [s.get('aret', '')] + [v for k, v in sorted(s.items()) if k.startswith('atp1')]
        return ' '.join(str(resolve(p, strings)) for p in parts)

    def slot_of(aid):
        # 1) research hotkey field, 2) "(Q)" in the learn/tooltip text with color codes removed
        hk = str(resolve(skin.get(aid, {}).get('arhk', ''), strings)).strip().upper()
        if hk[:1] in SLOTS and len(hk) >= 1:
            return hk[:1]
        plain = re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', text(aid))
        m = re.search(r'\(\s*([QWER])\s*\)', plain)
        return m.group(1) if m else None

    def passive(aid):
        o = abil.get(aid, {})
        levels = max(1, int(o.get('alev', 1)))
        base = stock.get(o.get('base', aid), [0.0] * 4)
        cds = [o.get('acdn%d' % lv, base[min(lv, 4) - 1]) for lv in range(1, levels + 1)]
        return max(cds) <= 0.0

    table = {}
    for uid, u in units.items():
        if not uid[0].isupper():
            continue
        habs = [a for a in str(u.get('uhab', '')).split(',') if a and a != STAT_BONUS]
        slots = {}
        for a in habs:
            s = slot_of(a)
            if s and s not in slots:
                slots[s] = a
        left = [a for a in habs if a not in slots.values()]
        free = [s for s in SLOTS if s not in slots]
        if len(left) == 1 and len(free) == 1:   # one skill without hotkey text -> the one free slot
            slots[free[0]] = left[0]
        if len(slots) == 4:
            table[uid] = [(s, slots[s], passive(slots[s])) for s in SLOTS]
    return table


if __name__ == '__main__':
    args = sys.argv[1:]
    game = None
    if '--game' in args:
        i = args.index('--game'); game = args[i + 1]; del args[i:i + 2]
    arc = Archive(args[0])
    strings = load_strings(arc)
    units = load_units(arc)
    t = skill_table(arc, game)
    script = arc.read('war3map.j').decode('utf-8', 'replace')
    roster = re.findall(r"set udg_Hero\[(?:\d+|\( udg_HeroMax\[1\] \+ \d+ \))\] = '(\w{4})'", script)
    missing = [h for h in roster if h not in t]
    for h in roster:
        if h in t:
            print(h, str(resolve(units[h].get('unam', h), strings)).strip()[:10],
                  ' '.join('%s:%s%s' % (s, a, '(P)' if p else '') for s, a, p in t[h]))
    print('roster', len(roster), 'mapped', len(roster) - len(missing), 'missing', missing, '| total unit types', len(t))
