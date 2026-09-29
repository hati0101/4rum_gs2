"""Minimal MPQ (v1) reader/writer for Warcraft III map files (.w3x / .w3m).

Supports what these maps actually use: hash/block tables, sector zlib/bzip2
compression, file encryption. Writing replaces existing files by appending new
data and a new block table (the hash table is left untouched).
"""
import bz2
import struct
import zlib

_CT = [0] * 0x500
_seed = 0x00100001
for _i in range(0x100):
    _idx = _i
    for _ in range(5):
        _seed = (_seed * 125 + 3) % 0x2AAAAB; _t1 = (_seed & 0xFFFF) << 16
        _seed = (_seed * 125 + 3) % 0x2AAAAB; _t2 = _seed & 0xFFFF
        _CT[_idx] = _t1 | _t2; _idx += 0x100

FLAG_EXISTS = 0x80000000
FLAG_COMPRESS = 0x00000200
FLAG_ENCRYPTED = 0x00010000
FLAG_FIX_KEY = 0x00020000
FLAG_SINGLE_UNIT = 0x01000000


def hash_string(s, kind):
    s1, s2 = 0x7FED7FED, 0xEEEEEEEE
    for c in s.upper().replace('/', '\\'):
        c = ord(c)
        s1 = (_CT[kind * 0x100 + c] ^ (s1 + s2)) & 0xFFFFFFFF
        s2 = (c + s1 + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return s1


def decrypt(data, key):
    s2 = 0xEEEEEEEE; out = []
    n = len(data) // 4
    for v in struct.unpack('<%dI' % n, data[:n * 4]):
        s2 = (s2 + _CT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        v ^= (key + s2) & 0xFFFFFFFF; out.append(v)
        key = ((~key << 0x15) + 0x11111111 | (key >> 0x0B)) & 0xFFFFFFFF
        s2 = (v + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return struct.pack('<%dI' % n, *out) + data[n * 4:]


def encrypt(data, key):
    s2 = 0xEEEEEEEE; out = []
    n = len(data) // 4
    for v in struct.unpack('<%dI' % n, data[:n * 4]):
        s2 = (s2 + _CT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        out.append(v ^ ((key + s2) & 0xFFFFFFFF))
        key = ((~key << 0x15) + 0x11111111 | (key >> 0x0B)) & 0xFFFFFFFF
        s2 = (v + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return struct.pack('<%dI' % n, *out) + data[n * 4:]


def _decompress(x, full):
    if len(x) == full:
        return x
    mask, x = x[0], x[1:]
    if mask == 0x02:
        return zlib.decompress(x)
    if mask == 0x10:
        return bz2.decompress(x)
    raise NotImplementedError('compression mask 0x%02x' % mask)


class Archive:
    def __init__(self, path):
        self.path = path
        self.data = open(path, 'rb').read()
        self.base = self.data.find(b'MPQ\x1a')
        if self.base < 0:
            raise ValueError('no MPQ header')
        b = self.base
        (_, _, _, sector_shift, ht_off, bt_off, ht_n, bt_n) = struct.unpack_from('<IIHHIIII', self.data, b + 4)
        self.sector_size = 512 << sector_shift
        raw = decrypt(self.data[b + ht_off:b + ht_off + ht_n * 16], hash_string('(hash table)', 3))
        self.hash_table = [struct.unpack_from('<IIHHI', raw, i * 16) for i in range(ht_n)]
        raw = decrypt(self.data[b + bt_off:b + bt_off + bt_n * 16], hash_string('(block table)', 3))
        self.block_table = [list(struct.unpack_from('<IIII', raw, i * 16)) for i in range(bt_n)]

    def find(self, name):
        a, b = hash_string(name, 1), hash_string(name, 2)
        n = len(self.hash_table); start = hash_string(name, 0) % n
        for k in range(n):
            e = self.hash_table[(start + k) % n]
            if e[4] == 0xFFFFFFFF:
                return None
            if e[0] == a and e[1] == b and e[4] < len(self.block_table):
                return e[4]
        return None

    def __contains__(self, name):
        return self.find(name) is not None

    def read(self, name):
        bi = self.find(name)
        if bi is None:
            return None
        off, csize, fsize, flags = self.block_table[bi]
        p = self.base + off
        key = None
        if flags & FLAG_ENCRYPTED:
            key = hash_string(name.replace('/', '\\').split('\\')[-1], 3)
            if flags & FLAG_FIX_KEY:
                key = ((key + off) ^ fsize) & 0xFFFFFFFF
        if flags & FLAG_SINGLE_UNIT:
            x = self.data[p:p + csize]
            if key is not None:
                x = decrypt(x, key)
            return _decompress(x, fsize) if flags & FLAG_COMPRESS else x
        if not flags & FLAG_COMPRESS:
            x = self.data[p:p + fsize]
            return decrypt(x, key) if key is not None else x
        ns = (fsize + self.sector_size - 1) // self.sector_size
        tbl = self.data[p:p + (ns + 1) * 4]
        if key is not None:
            tbl = decrypt(tbl, (key - 1) & 0xFFFFFFFF)
        offs = struct.unpack('<%dI' % (ns + 1), tbl)
        out = bytearray()
        for i in range(ns):
            x = self.data[p + offs[i]:p + offs[i + 1]]
            if key is not None:
                x = decrypt(x, (key + i) & 0xFFFFFFFF)
            out += _decompress(x, min(self.sector_size, fsize - i * self.sector_size))
        return bytes(out)

    def _pack(self, data):
        ss = self.sector_size
        ns = (len(data) + ss - 1) // ss
        sectors = []
        for i in range(ns):
            raw = data[i * ss:(i + 1) * ss]
            c = b'\x02' + zlib.compress(raw, 9)
            sectors.append(c if len(c) < len(raw) else raw)
        off = (ns + 1) * 4; offs = [off]
        for s in sectors:
            off += len(s); offs.append(off)
        return struct.pack('<%dI' % (ns + 1), *offs) + b''.join(sectors)

    def save_with_replacements(self, out_path, replacements):
        """Write a copy of the archive with existing files replaced.

        replacements: {name: bytes}. Every name must already exist in the archive.
        The (attributes) CRC32 table is updated for replaced files when present.
        """
        replacements = dict(replacements)
        attr_bi = self.find('(attributes)')
        if attr_bi is not None and '(attributes)' not in replacements:
            attr = bytearray(self.read('(attributes)'))
            ver, aflags = struct.unpack_from('<II', attr, 0)
            if ver == 100 and aflags & 1:
                for name, data in replacements.items():
                    struct.pack_into('<I', attr, 8 + 4 * self.find(name), zlib.crc32(data) & 0xFFFFFFFF)
                replacements['(attributes)'] = bytes(attr)
        buf = bytearray(self.data)
        bt = [list(b) for b in self.block_table]
        for name, data in replacements.items():
            bi = self.find(name)
            if bi is None:
                raise KeyError('not in archive: ' + name)
            blob = self._pack(data)
            bt[bi] = [len(buf) - self.base, len(blob), len(data), FLAG_EXISTS | FLAG_COMPRESS]
            buf += blob
        bt_off = len(buf) - self.base
        buf += encrypt(b''.join(struct.pack('<IIII', *b) for b in bt), hash_string('(block table)', 3))
        struct.pack_into('<I', buf, self.base + 8, len(buf) - self.base)   # archive size
        struct.pack_into('<I', buf, self.base + 20, bt_off)                # block table offset
        with open(out_path, 'wb') as f:
            f.write(buf)
