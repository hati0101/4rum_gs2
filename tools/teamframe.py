"""Build and inject the GSTF team panel (src/TeamFrame.template.j).

usage:
  python teamframe.py gen <map.w3x>
      writes src/TeamFrame.j (template + ultimate table generated from the map)
  python teamframe.py inject <in.w3x> <out.w3x> [--autostart] [--show-self]
      appends src/TeamFrame.j to the map's custom script header, in both
      war3map.wct (what the World Editor loads) and war3map.j (what the game runs).
      --autostart also adds `call GSTF_Init()` to main() in war3map.j so the panel
      runs without a trigger. This is for test builds: the World Editor rebuilds
      war3map.j on save, so a saved map needs a Map Initialization trigger with
      the custom script line `call GSTF_Init()`.
      --show-self lists the local player's own hero too (handy for solo tests).
      --test adds src/TeamFrameTest.j (-gstest / -gskill bot commands); needs --autostart.
      --pickflow adds src/PickFlow.j (host mode popup + hero board); a saved map
      needs `call GSPF_Init()` in the same Map Initialization trigger.
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
TEST_CODE = os.path.join(ROOT, 'src', 'TeamFrameTest.j')
MARKER = '//@@ULT_TABLE@@'
PICK_TEMPLATE = os.path.join(ROOT, 'src', 'PickFlow.template.j')
PICK_OUTPUT = os.path.join(ROOT, 'src', 'PickFlow.j')
PICK_MARKER = '//@@PICK_TABLE@@'
# shop name -> column order and label on the hero board (힘 / 민첩 / 지능)
ATTR_ORDER = {'힘': 0, '기민': 1, '지식': 2}
ATTR_LABEL = {'힘': '|cffff6060힘|r', '기민': '|cff60ff60민첩|r', '지식': '|cff60a0ff지능|r'}


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


def pick_table(arc):
    """JASS tables for the hero board: heroes grouped by the shop that sells them.

    Groups: Guardian shops first, then Darkness, each in shop-id order. Side comes
    from the roster in the init script (first udg_HeroMax[1] heroes = Guardian)."""
    from objdata import load_strings, resolve
    script = arc.read('war3map.j').decode('utf-8', 'replace')
    roster = [uid for _, uid in re.findall(r"set udg_Hero\[(\d+|\( udg_HeroMax\[1\] \+ \d+ \))\] = '(\w{4})'", script)]
    n_guard = int(re.search(r'set udg_HeroMax\[1\] = (\d+)', script).group(1))
    guardian = set(roster[:n_guard])
    units, strings = load_units(arc), load_strings(arc)
    shops = []
    for sid, u in sorted(units.items()):
        sold = [h for h in str(u.get('useu', '')).split(',') if h in roster]
        var = re.search(r'\b(gg_unit_%s_\d+)\b' % re.escape(sid), script)
        if sold and var:
            name = str(resolve(u.get('unam', sid), strings)).strip().replace('의 정령', '')
            shops.append((sold[0] not in guardian, ATTR_ORDER.get(name, 9), sid, var.group(1), name, sold))
    shops.sort()
    shops = [(s[0], s[2], s[3], ATTR_LABEL.get(s[4], s[4]), s[5]) for s in shops]
    heroes = [(g, h) for g, s in enumerate(shops) for h in s[4]]
    missing = [h for h in roster if h not in {h for _, h in heroes}]
    L = ['// 영웅 선택 보드 표 (tools/teamframe.py gen 으로 생성)',
         'function GSPF_HeroCount takes nothing returns integer',
         '    return %d' % len(heroes), 'endfunction', '',
         'function GSPF_HeroAt takes integer i returns integer']
    for i, (g, h) in enumerate(heroes):
        L += ["    %s i == %d then" % ('if' if i == 0 else 'elseif', i), "        return '%s'" % h]
    L += ['    endif', '    return 0', 'endfunction', '',
          'function GSPF_GroupOf takes integer i returns integer']
    start = 0
    for g, s in enumerate(shops):
        start += len(s[4])
        L += ['    if i < %d then' % start, '        return %d' % g, '    endif']
    L += ['    return %d' % (len(shops) - 1), 'endfunction', '',
          'function GSPF_Shop takes integer g returns unit']
    for g, s in enumerate(shops):
        L += ['    %s g == %d then' % ('if' if g == 0 else 'elseif', g), '        return %s' % s[2]]
    L += ['    endif', '    return null', 'endfunction', '',
          'function GSPF_GroupLabel takes integer g returns string']
    for g, s in enumerate(shops):
        L += ['    %s g == %d then' % ('if' if g == 0 else 'elseif', g),
              '        return "%s"' % s[3]]
    L += ['    endif', '    return ""', 'endfunction', '',
          'function GSPF_SideName takes integer s returns string',
          '    if s == 0 then', '        return "|cff70b0ff가디언|r"', '    endif',
          '    return "|cffff7070다크니스|r"', 'endfunction']
    assert len(shops) == 6 and [s[0] for s in shops] == [False] * 3 + [True] * 3, 'expected 3 shops per side'
    return '\n'.join(L), len(heroes), len(shops), missing


def gen(map_path):
    arc = Archive(map_path)
    table, n = ult_table(arc)
    src = open(TEMPLATE, encoding='utf-8').read()
    assert MARKER in src
    with open(OUTPUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src.replace(MARKER, table))
    print('wrote %s (%d hero types)' % (OUTPUT, n))
    table, n, shops, missing = pick_table(arc)
    src = open(PICK_TEMPLATE, encoding='utf-8').read()
    assert PICK_MARKER in src
    with open(PICK_OUTPUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src.replace(PICK_MARKER, table))
    print('wrote %s (%d heroes in %d shops, not sold: %s)' % (PICK_OUTPUT, n, shops, missing or 'none'))


def _eol(text):
    return '\r\n' if '\r\n' in text else '\n'


def inject_j(j, code, autostart, test=False, pickflow=False):
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
        calls = '    call GSTF_Init()' + eol
        if pickflow:
            calls += '    call GSPF_Init()' + eol
        if test:
            calls += '    call GSTF_TestInit()' + eol
        j = j[:mm.start(1)] + calls + j[mm.start(1):]
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


def inject(src, dst, autostart, show_self=False, test=False, pickflow=False):
    code = open(OUTPUT, encoding='utf-8').read().rstrip('\n')
    if show_self:
        old = 'function GSTF_ShowSelf takes nothing returns boolean\n    return false'
        assert old in code
        code = code.replace(old, old[:-5] + 'true')
    if pickflow:
        code += '\n\n' + open(PICK_OUTPUT, encoding='utf-8').read().rstrip('\n')
    if test:
        if not autostart:
            raise SystemExit('--test needs --autostart')
        code += '\n\n' + open(TEST_CODE, encoding='utf-8').read().rstrip('\n')
    arc = Archive(src)
    j = arc.read('war3map.j').decode('utf-8')
    wct = arc.read('war3map.wct')
    arc.save_with_replacements(dst, {
        'war3map.j': inject_j(j, code, autostart, test, pickflow).encode('utf-8'),
        'war3map.wct': inject_wct(wct, code),
    })
    flags = [f for f, on in (('autostart', autostart), ('show-self', show_self), ('test', test),
                             ('pickflow', pickflow)) if on]
    print('wrote', dst, '(%s)' % ', '.join(flags) if flags else '')


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == 'gen':
        gen(a[1])
    elif len(a) >= 3 and a[0] == 'inject':
        inject(a[1], a[2], '--autostart' in a, '--show-self' in a, '--test' in a, '--pickflow' in a)
    else:
        sys.exit(__doc__)
