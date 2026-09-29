"""Syntax-check a map's war3map.j with pjass against the game's own common.j/blizzard.j.

usage: python check_jass.py <pjass dir> <map.w3x> [<map.w3x> ...]
  <pjass dir> holds pjass.exe and game/common.j, game/blizzard.j
  (extract those with game_scripts.py from the installed game)
"""
import os
import subprocess
import sys

from w3x import Archive

tool = sys.argv[1]
ok = True
for path in sys.argv[2:]:
    j = os.path.join(tool, '_check.j')
    with open(j, 'wb') as f:
        f.write(Archive(path).read('war3map.j'))
    r = subprocess.run([os.path.join(tool, 'pjass.exe'), '+shadow', '+rb',
                        os.path.join(tool, 'game', 'common.j'), os.path.join(tool, 'game', 'blizzard.j'), j],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr
    errors = [l for l in r.stdout.splitlines() if 'Parse successful' not in l]
    print('%s: %s' % (os.path.basename(path), last))
    for l in errors[:20]:
        print('   ', l)
    ok = ok and r.returncode == 0
sys.exit(0 if ok else 1)
