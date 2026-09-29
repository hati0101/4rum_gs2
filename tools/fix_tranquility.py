"""Fix unintended caster invulnerability on Tranquility-based abilities.

A later patch added the Tranquility field Etq4 "Initial Immunity Duration"
(DataD). Stock values are 0 at level 1 and 1 second at levels 2+. Abilities
based on Tranquility (AEtq) that were made before the field existed never set
it, so from level 2 their caster is invulnerable for 1 second on cast
(e.g. 오우거 로드 파워 스트라이크). This sets Etq4 = 0 on every level of every
AEtq-based custom ability.

usage: python fix_tranquility.py <input.w3x> <output.w3x>
"""
import struct
import sys

from objdata import iter_mods
from w3x import Archive

BASE = 'AEtq'
FIELD = b'Etq4'
DATA_PTR = 4           # DataD
TYPE_UNREAL = 2


def fix(data):
    """Return (new w3a data, [(ability id, levels)])."""
    ver, = struct.unpack_from('<I', data, 0)
    tables = [[], []]
    fixed = []
    for table, orig, new, set_idx, flag, mods in iter_mods(data, leveled=True):
        raws = [m['raw'] for m in mods]
        if table == 1 and orig == BASE and set_idx == 0 and mods:
            # alev, or higher if some field has data for a higher level (talents may raise it)
            levels = max([next((m['value'] for m in mods if m['id'] == 'alev'), 1)] + [m['level'] for m in mods])
            end = mods[0]['raw'][-4:]
            raws = [m['raw'] for m in mods if m['id'] != FIELD.decode()]
            for lv in range(1, levels + 1):
                raws.append(FIELD + struct.pack('<IIIf', TYPE_UNREAL, lv, DATA_PTR, 0.0) + end)
            fixed.append((new, levels))
        if set_idx == 0:
            tables[table].append((orig, new, []))
        tables[table][-1][2].append((flag, raws))

    out = bytearray(struct.pack('<I', ver))
    for objects in tables:
        out += struct.pack('<I', len(objects))
        for orig, new, sets in objects:
            out += orig.encode('latin1') + new.encode('latin1')
            if ver >= 3:
                out += struct.pack('<I', len(sets))
            for flag, raws in sets:
                if ver >= 3:
                    out += struct.pack('<I', flag)
                out += struct.pack('<I', len(raws)) + b''.join(raws)
    return bytes(out), fixed


def main(src, dst):
    arc = Archive(src)
    new_data, fixed = fix(arc.read('war3map.w3a'))
    for aid, levels in fixed:
        print('Etq4 = 0  %s  (levels 1-%d)' % (aid, levels))
    print('%d abilities fixed' % len(fixed))
    if fixed:
        arc.save_with_replacements(dst, {'war3map.w3a': new_data})
        print('wrote', dst)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
