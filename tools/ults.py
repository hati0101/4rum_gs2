"""Identify each roster hero's ultimate ability.

Rule: among the hero's abilities (uhab), the ultimate is the one whose required
hero level (arlv) is 6; if none has arlv set, the one with 3 levels (alev).
Heroes with no or several candidates are reported as ambiguous.

usage: python ults.py <map.w3x>          # print table
       python ults.py <map.w3x> --jass   # print JASS init lines
"""
import re
import sys

from objdata import load_objects, load_strings, load_units, resolve
from w3x import Archive

STAT_BONUS = 'A04T'  # 속성 보너스 (shared by all heroes)


def roster(script):
    """[(roster index expr, hero id)] in udg_Hero order."""
    return re.findall(r"set udg_Hero\[(\d+|\( udg_HeroMax\[1\] \+ \d+ \))\] = '(\w{4})'", script)


def find_ults(arc):
    strings = load_strings(arc)
    units = load_units(arc)
    abil = load_objects(arc, 'war3map.w3a')
    skin = load_objects(arc, 'war3mapSkin.w3a')
    script = arc.read('war3map.j').decode('utf-8', 'replace')
    result = []
    for idx, uid in roster(script):
        u = units.get(uid, {})
        habs = [a for a in str(u.get('uhab', '')).split(',') if a and a != STAT_BONUS]
        cands = [a for a in habs if abil.get(a, {}).get('arlv') == 6]
        if not cands:
            cands = [a for a in habs if abil.get(a, {}).get('alev') == 3]
        name = lambda a: str(resolve(skin.get(a, {}).get('anam', abil.get(a, {}).get('anam', a)), strings)).strip()
        hero = str(resolve(u.get('unam', uid), strings)).strip()
        result.append((idx, uid, hero, cands, [name(a) for a in cands]))
    return result


def main(path, jass):
    rows = find_ults(Archive(path))
    for idx, uid, hero, cands, names in rows:
        if jass:
            if len(cands) == 1:
                print("    set udg_TF_Ult[%s] = '%s' // %s: %s" % (idx, cands[0], hero, names[0]))
            else:
                print("    // TODO %s %s: ultimate not identified %s" % (idx, uid, cands))
        else:
            flag = '' if len(cands) == 1 else '  <-- AMBIGUOUS'
            print('%-26s %s %-14s %s %s%s' % (idx, uid, hero, cands, names, flag))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], '--jass' in sys.argv)
