"""Extract the installed game's own scripts/common.j and scripts/blizzard.j.

usage: python game_scripts.py "D:\\Warcraft III" <outdir>
"""
import os
import sys

from casc import Casc

c = Casc(sys.argv[1])
want = {'war3.w3mod:scripts/common.j': 'common.j', 'war3.w3mod:scripts/blizzard.j': 'blizzard.j'}
for line in c.root().decode('utf-8', 'replace').splitlines():
    parts = line.split('|')
    key = parts[0].lower()
    if key in want:
        data = c.read_ckey(bytes.fromhex(parts[1]))
        with open(os.path.join(sys.argv[2], want[key]), 'wb') as f:
            f.write(data)
        print(key, len(data), 'version', c.version)
