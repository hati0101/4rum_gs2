"""Build and inject the GSTF team panel (src/TeamFrame.template.j).

usage:
  python teamframe.py gen <map.w3x>
      writes src/TeamFrame.j (template + ultimate table generated from the map)
  python teamframe.py inject <in.w3x> <out.w3x> [--autostart]
      appends src/TeamFrame.j to the map's custom script header, in both
      war3map.wct (what the World Editor loads) and war3map.j (what the game runs).
      --autostart also adds `call GSTF_Init()` to main() in war3map.j so the panel
      runs without a trigger. This is for test builds: the World Editor rebuilds
      war3map.j on save, so a saved map needs a Map Initialization trigger with
      the custom script line `call GSTF_Init()`.
"""
import os
import re
import struct
import sys

from objdata import load_units
from ults import find_ults
from w3x import Archive

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'src', 'TeamFrame.template.j')
OUTPUT = os.path.join(ROOT, 'src', 'TeamFrame.j')
MARKER = '//@@ULT_TABLE@@'


def ult_table(arc):
    """JASS function mapping hero unit type -> ultimate ability id.

    Covers roster heroes and any other hero-type unit (alternate forms) whose
    ability list contains one of the roster ultimates."""
    ults = {}
    for _, uid, hero, cands, _ in find_ults(arc):
        if len(cands) == 1:
            ults[uid] = (cands[0], hero)
    ult_ids = {a for a, _ in ults.values()}
    for uid, u in load_units(arc).items():
        if uid in ults or not uid[0].isupper():
            continue
        habs = set(str(u.get('uhab', '')).split(','))
        hit = sorted(habs & ult_ids)
        if len(hit) == 1:
            ults[uid] = (hit[0], '(형태) ' + uid)
    lines = ['// 영웅 유닛 타입 -> 궁극기 (tools/teamframe.py gen 으로 생성)',
             'function GSTF_UltOf takes integer t returns integer']
    for n, (uid, (abil, hero)) in enumerate(ults.items()):
        kw = 'if' if n == 0 else 'elseif'
        lines.append("    %s t == '%s' then // %s" % (kw, uid, hero))
        lines.append("        return '%s'" % abil)
    lines += ['    endif', '    return 0', 'endfunction']
    return '\n'.join(lines), len(ults)


def gen(map_path):
    arc = Archive(map_path)
    table, n = ult_table(arc)
    src = open(TEMPLATE, encoding='utf-8').read()
    assert MARKER in src
    with open(OUTPUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src.replace(MARKER, table))
    print('wrote %s (%d hero types)' % (OUTPUT, n))


def _eol(text):
    return '\r\n' if '\r\n' in text else '\n'


def inject_j(j, code, autostart):
    eol = _eol(j)
    if 'function GSTF_Init' in j:
        raise SystemExit('war3map.j already contains GSTF')
    # map header = the "Custom Script Code" section right before "Triggers"
    m = re.search(r'(//\*+\r?\n//\*\r?\n//\*  Triggers)', j)
    if not m:
        raise SystemExit('Triggers section not found')
    body = code.replace('\n', eol)
    j = j[:m.start()] + body + eol + eol + j[m.start():]
    if autostart:
        mm = re.search(r'function main takes nothing returns nothing.*?\n(endfunction)', j, re.S)
        j = j[:mm.start(1)] + '    call GSTF_Init()' + eol + j[mm.start(1):]
    return j


def inject_wct(wct, code):
    ver, sub = struct.unpack_from('<II', wct, 0)
    if ver != 0x80000004 or sub != 1:
        raise SystemExit('unsupported wct version %x/%d' % (ver, sub))
    p = 8
    p = wct.index(b'\0', p) + 1           # header comment
    n, = struct.unpack_from('<I', wct, p)
    head = wct[p + 4:p + 4 + n]
    term = b'\0' if head.endswith(b'\0') else b''
    text = head[:len(head) - len(term)].decode('utf-8')
    if 'function GSTF_Init' in text:
        raise SystemExit('wct already contains GSTF')
    eol = _eol(text) if text else '\r\n'
    new = (text.rstrip('\r\n') + eol + eol + code.replace('\n', eol) + eol).encode('utf-8') + term
    return wct[:p] + struct.pack('<I', len(new)) + new + wct[p + 4 + n:]


def inject(src, dst, autostart):
    code = open(OUTPUT, encoding='utf-8').read().rstrip('\n')
    arc = Archive(src)
    j = arc.read('war3map.j').decode('utf-8')
    wct = arc.read('war3map.wct')
    arc.save_with_replacements(dst, {
        'war3map.j': inject_j(j, code, autostart).encode('utf-8'),
        'war3map.wct': inject_wct(wct, code),
    })
    print('wrote', dst, '(autostart)' if autostart else '')


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == 'gen':
        gen(a[1])
    elif len(a) >= 3 and a[0] == 'inject':
        inject(a[1], a[2], '--autostart' in a)
    else:
        sys.exit(__doc__)
