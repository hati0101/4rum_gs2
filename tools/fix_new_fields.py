"""Neutralize ability fields added by later patches that old custom abilities never set.

When a patch adds a field, custom abilities made before it inherit the stock
value. Some stock values are 0 on low levels but non-zero on higher levels,
which silently changes how the old ability works from that level on.
Find more with tools/audit_stock_levels.py.

Rules (field set to 0 on every level of every custom ability with that base):
  AEtq Etq4  Tranquility  "Initial Immunity Duration"  stock 1s from level 2
             -> caster invulnerable for 1s (오우거 로드 파워 스트라이크 등 6개)
  AHtc Htc5  Thunder Clap "Maximum Damage"             stock 1400 from level 4
             -> total damage capped at 1400 (크루스닉 그랜드 크로스 등 31개);
                0 = no cap, same as levels 1-3

usage: python fix_new_fields.py <input.w3x> <output.w3x>
"""
import struct
import sys

from objdata import iter_mods
from w3x import Archive

TYPE_UNREAL = 2
# base ability, field id, data pointer (DataA=1 ... DataE=5)
RULES = [
    ('AEtq', 'Etq4', 4),
    ('AHtc', 'Htc5', 5),
]
MIN_LEVELS = 4   # stock data defines 4 levels; cover them even if alev is lower


def fix(data):
    """Return (new w3a data, [(ability id, field, levels)])."""
    ver, = struct.unpack_from('<I', data, 0)
    rules = {base: (fid, ptr) for base, fid, ptr in RULES}
    tables = [[], []]
    fixed = []
    for table, orig, new, set_idx, flag, mods in iter_mods(data, leveled=True):
        raws = [m['raw'] for m in mods]
        if table == 1 and orig in rules and set_idx == 0 and mods:
            fid, ptr = rules[orig]
            # alev, or higher if some field has data for a higher level (talents may raise it)
            levels = max([next((m['value'] for m in mods if m['id'] == 'alev'), 1), MIN_LEVELS]
                         + [m['level'] for m in mods])
            end = mods[0]['raw'][-4:]
            raws = [m['raw'] for m in mods if m['id'] != fid]
            for lv in range(1, levels + 1):
                raws.append(fid.encode() + struct.pack('<IIIf', TYPE_UNREAL, lv, ptr, 0.0) + end)
            fixed.append((new, fid, levels))
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
    count = {}
    for aid, fid, levels in fixed:
        count[fid] = count.get(fid, 0) + 1
    for fid, n in count.items():
        print('%s = 0: %d abilities' % (fid, n))
    if fixed:
        arc.save_with_replacements(dst, {'war3map.w3a': new_data})
        print('wrote', dst)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
