"""Fix hero portraits broken by Warcraft III 2.0.

Patch 2.0 added the unit field 'upor' (Art - Portrait Model File). Units whose
model ('umdl') was changed before 2.0 have no 'upor', so the game shows the
portrait of the base unit instead. This sets upor = umdl for every hero-type
unit (id starting with an uppercase letter) that has a custom model and no upor.

usage: python fix_portraits.py <input.w3x> <output.w3x>
"""
import struct
import sys

from objdata import iter_mods
from w3x import Archive

SKIP_MODELS = {'.mdl', 'none.mdl', ''}


def add_portraits(data):
    """Return (new object data, [(unit id, model)]) with upor added."""
    ver, = struct.unpack_from('<I', data, 0)
    tables = [[], []]  # per table: list of objects, each a list of (flag, [raw mods])
    patched = []
    for table, orig, new, set_idx, flag, mods in iter_mods(data, leveled=False):
        raws = [m['raw'] for m in mods]
        oid = new if new != '\0\0\0\0' else orig
        umdl = next((m for m in mods if m['id'] == 'umdl'), None)
        if (set_idx == 0 and oid[0].isupper() and umdl
                and not any(m['id'] == 'upor' for m in mods)
                and umdl['value'].strip().lower() not in SKIP_MODELS):
            end = umdl['raw'][-4:]
            raws.append(b'upor' + struct.pack('<I', 3) + umdl['value'].encode('utf-8') + b'\0' + end)
            patched.append((oid, umdl['value']))
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
    return bytes(out), patched


def main(src, dst):
    arc = Archive(src)
    name = 'war3mapSkin.w3u' if 'war3mapSkin.w3u' in arc else 'war3map.w3u'
    new_data, patched = add_portraits(arc.read(name))
    for oid, mdl in patched:
        print('upor', oid, mdl)
    print('%d units patched in %s' % (len(patched), name))
    if patched:
        arc.save_with_replacements(dst, {name: new_data})
        print('wrote', dst)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
