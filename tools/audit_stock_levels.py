"""Find ability fields that silently take an odd stock value at some levels.

Pattern behind two bugs so far (Tranquility Etq4, Thunder Clap Htc5): a field
added in a later patch whose stock value is 0 on low levels but non-zero on a
higher level. Custom abilities made before the field existed never set it, so
their higher levels inherit the stock value.

Reports, for each custom ability, Data fields (DataA..DataI) where the map does
not set a level it uses and the stock value on that level differs from the
stock level-1 value while level 1 is 0.

usage: python audit_stock_levels.py <map.w3x> "D:\\Warcraft III"
"""
import sys
from collections import defaultdict

from casc import Casc
from objdata import load_objects, load_strings, resolve
from w3x import Archive

DATA = 'ABCDEFGHI'


def read_slk(text):
    rows, cur = {}, None
    for ln in text.splitlines():
        if ln.startswith('C;'):
            parts = dict((x[0], x[1:]) for x in ln.split(';')[1:] if x)
            if 'Y' in parts:
                cur = int(parts['Y'])
            rows.setdefault(cur, {})[int(parts['X'])] = parts.get('K', '').strip('"')
    hdr = rows.pop(1)
    return [{hdr.get(k, k): v for k, v in r.items()} for r in rows.values()]


def main(map_path, game_dir):
    c = Casc(game_dir)
    files = {}
    for line in c.root().decode('utf-8', 'replace').splitlines():
        p = line.split('|')
        if len(p) > 1:
            files[p[0].lower()] = p[1]
    get = lambda n: c.read_ckey(bytes.fromhex(files[n])).decode('utf-8', 'replace')
    stock = {r['alias']: r for r in read_slk(get('war3.w3mod:units/abilitydata.slk')) if r.get('alias')}
    meta = [r for r in read_slk(get('war3.w3mod:units/abilitymetadata.slk')) if r.get('field') == 'Data']
    names = {}
    for ln in get('war3.w3mod:_locales/kokr.w3mod:ui/worldeditstrings.txt').splitlines():
        k, _, v = ln.partition('=')
        names[k] = v
    # (base, data letter) -> field id (e.g. ('AHtc', 'E') -> 'Htc5')
    field_of = {}
    for m in meta:
        letter = DATA[int(m['data']) - 1] if m.get('data', '').isdigit() and 0 < int(m['data']) <= 9 else None
        for base in (m.get('useSpecific') or '').split(','):
            if letter and base:
                field_of[(base, letter)] = (m['ID'], names.get(m.get('displayName', ''), m['ID']))

    arc = Archive(map_path)
    strings = load_strings(arc)
    abil = load_objects(arc, 'war3map.w3a')
    skin = load_objects(arc, 'war3mapSkin.w3a')
    hits = defaultdict(list)
    for aid, o in abil.items():
        base = o.get('base')
        row = stock.get(base)
        if not row or not o.get('custom'):
            continue
        levels = int(o.get('alev', row.get('levels') or 1) or 1)
        levels = max([levels] + [int(k[4:]) for k in o if k[:4] in {f for f, _ in field_of.values()} and k[4:].isdigit()])
        for letter in DATA:
            fid = field_of.get((base, letter))
            if not fid:
                continue
            def sv(lv):
                v = row.get('Data%s%d' % (letter, min(lv, 4)), '')
                try:
                    return float(v or 0)
                except ValueError:
                    return None
            if sv(1) != 0:
                continue
            for lv in range(2, levels + 1):
                if '%s%d' % (fid[0], lv) in o:
                    continue
                s = sv(lv)
                if s not in (None, 0.0):
                    hits[(base, fid)].append((aid, lv, s))
    for (base, (fid, label)), rows in sorted(hits.items()):
        ids = sorted({a for a, _, _ in rows})
        print('%s %s "%s": %d개 능력' % (base, fid, label, len(ids)))
        for aid in ids:
            lv = [(l, s) for a, l, s in rows if a == aid]
            nm = str(resolve(skin.get(aid, {}).get('atp11', skin.get(aid, {}).get('anam', '')), strings)).strip()
            print('   %s %-30s 원본값이 들어가는 레벨: %s' % (aid, nm[:30], ', '.join('%d레벨=%g' % x for x in lv)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
