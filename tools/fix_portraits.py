"""Fix hero portraits broken by Warcraft III 2.0.

Patch 2.0 added the unit field 'upor' (Art - Portrait Model File). Units whose
model ('umdl') was changed before 2.0 have no 'upor', so the game shows the
portrait of the base unit instead.

The game uses 'upor' literally as the portrait model (it does not append
"_portrait"), so for a stock model X.mdl we set upor = X_portrait.mdl, the
separate portrait model that carries the face camera. Models imported into
the map have no separate portrait, so they get upor = the model itself.

Applies to every hero-type unit (id starting with an uppercase letter) with a
custom model; an existing upor is replaced.

usage: python fix_portraits.py <input.w3x> <output.w3x> [--game "D:\\Warcraft III"]
       --game checks every portrait path against the installed game's files
"""
import re
import struct
import sys

from objdata import iter_mods
from w3x import Archive

SKIP_MODELS = {'.mdl', 'none.mdl', ''}


def portrait_for(model, arc):
    """Portrait model path for a unit model path."""
    stem = re.sub(r'\.(mdl|mdx)$', '', model, flags=re.I)
    if arc.find(stem + '.mdx') is not None or arc.find(stem + '.mdl') is not None:
        return model                      # imported model: no separate portrait file
    return stem + '_portrait.mdl'


def add_portraits(data, arc):
    """Return (new object data, [(unit id, model, portrait)]) with upor set."""
    ver, = struct.unpack_from('<I', data, 0)
    tables = [[], []]  # per table: list of objects, each a list of (flag, [raw mods])
    patched = []
    for table, orig, new, set_idx, flag, mods in iter_mods(data, leveled=False):
        oid = new if new != '\0\0\0\0' else orig
        umdl = next((m for m in mods if m['id'] == 'umdl'), None)
        if (set_idx == 0 and oid[0].isupper() and umdl
                and umdl['value'].strip().lower() not in SKIP_MODELS):
            mods = [m for m in mods if m['id'] != 'upor']
            raws = [m['raw'] for m in mods]
            por = portrait_for(umdl['value'], arc)
            end = umdl['raw'][-4:]
            raws.append(b'upor' + struct.pack('<I', 3) + por.encode('utf-8') + b'\0' + end)
            patched.append((oid, umdl['value'], por))
        else:
            raws = [m['raw'] for m in mods]
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


def game_files(game_dir):
    """{'sd': set, 'hd': set} of lowercase model paths without extension."""
    from casc import Casc
    sd, hd = set(), set()
    for line in Casc(game_dir).root().decode('utf-8', 'replace').splitlines():
        path = line.split('|', 1)[0].lower()
        if not path.endswith('.mdx'):
            continue
        if path.startswith('war3.w3mod:_hd.w3mod:'):
            hd.add(path[len('war3.w3mod:_hd.w3mod:'):-4])
        elif path.startswith('war3.w3mod:') and not path.startswith('war3.w3mod:_'):
            sd.add(path[len('war3.w3mod:'):-4])
    return {'sd': sd, 'hd': hd}


def main(src, dst, game_dir=None):
    arc = Archive(src)
    name = 'war3mapSkin.w3u' if 'war3mapSkin.w3u' in arc else 'war3map.w3u'
    new_data, patched = add_portraits(arc.read(name), arc)
    files = game_files(game_dir) if game_dir else None
    for oid, mdl, por in patched:
        note = ''
        if files is not None and por != mdl:
            key = re.sub(r'\.(mdl|mdx)$', '', por.replace('\\', '/').lower())
            sd, hd = key in files['sd'], key in files['hd']
            note = '' if sd and hd else '  <-- only %s' % ('HD' if hd else 'SD' if sd else 'MISSING')
        print('upor %s %s%s' % (oid, por, note))
    print('%d units patched in %s' % (len(patched), name))
    if patched:
        arc.save_with_replacements(dst, {name: new_data})
        print('wrote', dst)


if __name__ == '__main__':
    args = sys.argv[1:]
    game = None
    if '--game' in args:
        i = args.index('--game'); game = args[i + 1]; del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    main(args[0], args[1], game)
