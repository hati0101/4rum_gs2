"""Minimal local CASC reader for an installed Warcraft III (Reforged).

Only what's needed to list game files and read small ones:
build config -> encoding (ckey -> ekey) -> local .idx (ekey -> data.NNN offset) -> BLTE.

usage: python casc.py "D:\\Warcraft III" [substring]   # list file names containing substring
"""
import glob
import os
import struct
import sys
import zlib


def _blte(data):
    assert data[:4] == b'BLTE', data[:4]
    hsize, = struct.unpack_from('>I', data, 4)
    if hsize == 0:
        chunks = [(len(data) - 8, None)]
        p = 8
    else:
        count = int.from_bytes(data[9:12], 'big')
        chunks = [struct.unpack_from('>II', data, 12 + i * 24) for i in range(count)]
        p = hsize
    out = bytearray()
    for c in chunks:
        csize = c[0]
        blk = data[p:p + csize]; p += csize
        mode = blk[:1]
        if mode == b'N':
            out += blk[1:]
        elif mode == b'Z':
            out += zlib.decompress(blk[1:])
        else:
            raise NotImplementedError('BLTE mode %r' % mode)
    return bytes(out)


class Casc:
    def __init__(self, root_dir):
        self.dir = os.path.join(root_dir, 'Data')
        info = open(os.path.join(root_dir, '.build.info'), encoding='utf-8').read().splitlines()
        cols = [c.split('!')[0] for c in info[0].split('|')]
        row = dict(zip(cols, info[1].split('|')))
        self.version = row.get('Version')
        bk = row['Build Key']
        cfg = open(os.path.join(self.dir, 'config', bk[:2], bk[2:4], bk), encoding='utf-8').read()
        self.config = {}
        for line in cfg.splitlines():
            if ' = ' in line:
                k, v = line.split(' = ', 1)
                self.config[k] = v.split()
        self._load_indices()
        enc_ekey = bytes.fromhex(self.config['encoding'][1])
        self.encoding = self._parse_encoding(self.read_ekey(enc_ekey))

    def _load_indices(self):
        self.index = {}
        files = sorted(glob.glob(os.path.join(self.dir, 'data', '*.idx')))
        latest = {}
        for f in files:                      # keep the newest version per bucket
            b = os.path.basename(f)[:2]
            latest[b] = f
        for f in latest.values():
            d = open(f, 'rb').read()
            size, = struct.unpack_from('<I', d, 0x20)
            p = 0x28
            for _ in range(size // 18):
                key = d[p:p + 9]
                v = int.from_bytes(d[p + 9:p + 14], 'big')
                n, = struct.unpack_from('<I', d, p + 14)
                self.index.setdefault(key, (v >> 30, v & 0x3FFFFFFF, n))
                p += 18

    def read_ekey(self, ekey):
        arc, off, size = self.index[ekey[:9]]
        with open(os.path.join(self.dir, 'data', 'data.%03d' % arc), 'rb') as f:
            f.seek(off)
            blob = f.read(size)
        return _blte(blob[0x1E:])

    @staticmethod
    def _parse_encoding(d):
        assert d[:2] == b'EN'
        ck, ek = d[3], d[4]
        psize, = struct.unpack_from('>H', d, 5)
        pcount, = struct.unpack_from('>I', d, 9)
        espec, = struct.unpack_from('>I', d, 18)
        p = 22 + espec + pcount * 32
        table = {}
        for _ in range(pcount):
            page = d[p:p + psize * 1024]; p += psize * 1024
            q = 0
            while q + 6 + ck <= len(page):
                n = page[q]
                if n == 0:
                    break
                ckey = page[q + 6:q + 6 + ck]
                table[ckey] = page[q + 6 + ck:q + 6 + ck + ek]
                q += 6 + ck + n * ek
        return table

    def read_ckey(self, ckey):
        return self.read_ekey(self.encoding[ckey])

    def root(self):
        return self.read_ckey(bytes.fromhex(self.config['root'][0]))


if __name__ == '__main__':
    c = Casc(sys.argv[1])
    r = c.root()
    print('version', c.version, 'root bytes', len(r))
    print(r[:600])
