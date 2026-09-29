"""Extract text data from a map so changes can be diffed in git.

Writes into <outdir>:
  war3map.j    map script
  war3map.wts  trigger strings
  heroes.md    hero roster per side (Guardian / Darkness) with model/portrait info

usage: python extract.py <map.w3x> <outdir>
"""
import os
import re
import sys

from objdata import load_strings, load_units, resolve
from w3x import Archive


def hero_rows(script, units, strings):
    """Parse the hero roster from the map init script."""
    guard = re.findall(r"set udg_Hero\[(\d+)\] = '(\w{4})'", script)
    dark = re.findall(r"set udg_Hero\[\( udg_HeroMax\[1\] \+ (\d+) \)\] = '(\w{4})'", script)
    gname = dict(re.findall(r'set udg_HeroName\[(\d+)\] = "([^"]*)"', script))
    dname = dict(re.findall(r'set udg_HeroName\[\( udg_HeroMax\[1\] \+ (\d+) \)\] = "([^"]*)"', script))
    for side, roster, names in (('가디언', guard, gname), ('다크니스', dark, dname)):
        rows = []
        for idx, uid in roster:
            u = units.get(uid, {})
            rows.append((idx, uid, str(resolve(u.get('unam', '(기본)'), strings)).strip(),
                         names.get(idx, ''), u.get('umdl', '(기본)'), u.get('upor', '')))
        yield side, rows


def main(path, outdir):
    arc = Archive(path)
    os.makedirs(outdir, exist_ok=True)
    for name in ('war3map.j', 'war3map.wts'):
        data = arc.read(name) or arc.read('scripts\\' + name)
        if data is not None:
            with open(os.path.join(outdir, name), 'wb') as f:
                f.write(data)
    strings = load_strings(arc)
    units = load_units(arc)
    script = arc.read('war3map.j').decode('utf-8', 'replace')
    lines = ['# 영웅 목록', '', '`tools/extract.py`로 자동 생성됨. 직접 수정하지 마세요.', '']
    for side, rows in hero_rows(script, units, strings):
        lines += ['## %s (%d)' % (side, len(rows)), '',
                  '| # | ID | 유닛 이름 | 영웅 이름 | 모델 | 초상화(upor) |',
                  '|---|---|---|---|---|---|']
        for r in rows:
            lines.append('| %s | `%s` | %s | %s | `%s` | %s |' % (r[0], r[1], r[2], r[3], r[4],
                                                             '`%s`' % r[5] if r[5] else ''))
        lines.append('')
    with open(os.path.join(outdir, 'heroes.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print('extracted to', outdir)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
