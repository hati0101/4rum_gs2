"""Warcraft III object data (.w3u/.w3t/.w3b/.w3h and .w3a/.w3d/.w3q) and .wts strings."""
import re
import struct

# files whose modifications carry level + data-pointer fields
LEVELED = ('.w3a', '.w3d', '.w3q')


def load_strings(archive):
    wts = archive.read('war3map.wts')
    table = {}
    if wts:
        text = wts.decode('utf-8', 'replace')
        for m in re.finditer(r'STRING (\d+)[ \t]*\r?\n(?://[^\n]*\n)?\{\r?\n(.*?)\r?\n\}', text, re.S):
            table[int(m.group(1))] = m.group(2)
    return table


def resolve(value, strings):
    if isinstance(value, str):
        m = re.fullmatch(r'TRIGSTR_(\d+)', value)
        if m:
            return strings.get(int(m.group(1)), value)
    return value


def iter_mods(data, leveled):
    """Yield (table, orig, new, set_index, set_flag, mods) where mods is a list of
    dicts {id, level, data, type, value, raw} and raw is the exact byte slice."""
    ver, = struct.unpack_from('<I', data, 0); p = 4
    for table in range(2):
        count, = struct.unpack_from('<I', data, p); p += 4
        for _ in range(count):
            orig = data[p:p + 4].decode('latin1'); new = data[p + 4:p + 8].decode('latin1'); p += 8
            nsets = 1
            if ver >= 3:
                nsets, = struct.unpack_from('<I', data, p); p += 4
            for s in range(nsets):
                flag = 0
                if ver >= 3:
                    flag, = struct.unpack_from('<I', data, p); p += 4
                n, = struct.unpack_from('<I', data, p); p += 4
                mods = []
                for _ in range(n):
                    st = p
                    fid = data[p:p + 4].decode('latin1'); p += 4
                    level = dptr = 0
                    if leveled:
                        level, dptr = struct.unpack_from('<II', data, p); p += 8
                    t, = struct.unpack_from('<I', data, p); p += 4
                    if t == 0:
                        v, = struct.unpack_from('<i', data, p); p += 4
                    elif t in (1, 2):
                        v, = struct.unpack_from('<f', data, p); p += 4
                    else:
                        e = data.index(b'\0', p); v = data[p:e].decode('utf-8', 'replace'); p = e + 1
                    p += 4  # end marker
                    mods.append({'id': fid, 'level': level, 'data': dptr, 'type': t, 'value': v, 'raw': data[st:p]})
                yield table, orig, new, s, flag, mods
    assert p == len(data), 'trailing bytes in object data'


def load_objects(archive, name):
    """{object_id: {'base': orig, 'custom': bool, field_id[+level]: value}}"""
    data = archive.read(name)
    if not data:
        return {}
    leveled = name.lower().endswith(LEVELED)
    objs = {}
    for table, orig, new, _, _, mods in iter_mods(data, leveled):
        oid = new if new != '\0\0\0\0' else orig
        o = objs.setdefault(oid, {'base': orig, 'custom': table == 1})
        for m in mods:
            o[m['id'] + (str(m['level']) if m['level'] else '')] = m['value']
    return objs


def load_units(archive):
    """Unit data merged from war3map.w3u and war3mapSkin.w3u (skin fields win)."""
    units = load_objects(archive, 'war3map.w3u')
    for oid, o in load_objects(archive, 'war3mapSkin.w3u').items():
        u = units.setdefault(oid, {'base': o['base'], 'custom': o['custom']})
        u.update({k: v for k, v in o.items() if k not in ('base', 'custom')})
    return units
