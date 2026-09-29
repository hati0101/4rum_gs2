"""Summarize an MDX model: version, sequences, textures, particle emitters (PRE2).

usage: python mdx_info.py <map.w3x> <model path in map>
"""
import struct
import sys

from w3x import Archive


def chunks(m):
    p = 4
    while p + 8 <= len(m):
        tag = m[p:p + 4].decode('latin1')
        n, = struct.unpack_from('<I', m, p + 4)
        yield tag, m[p + 8:p + 8 + n]
        p += 8 + n


def pre2(data):
    """Parse ParticleEmitter2 records (MDX 800)."""
    p = 0
    out = []
    while p < len(data):
        size, = struct.unpack_from('<I', data, p)
        rec = data[p:p + size]
        # node header
        nsize, = struct.unpack_from('<I', rec, 4)
        name = rec[8:8 + 80].split(b'\0')[0].decode('latin1')
        q = 4 + nsize
        speed, variation, latitude, gravity, lifespan, emission, width, length = struct.unpack_from('<8f', rec, q)
        q += 32
        filter_mode, rows, cols, head_or_tail = struct.unpack_from('<4I', rec, q)
        q += 16
        tail_length, time = struct.unpack_from('<2f', rec, q)
        q += 8
        q += 36          # segment colors 3x3 floats
        q += 3           # segment alphas
        q += 12          # segment scaling
        q += 48          # head/tail intervals
        texture_id, squirt, priority, replaceable = struct.unpack_from('<Ii Ii', rec, q)[:4] if False else struct.unpack_from('<IIiI', rec, q)
        out.append({'name': name, 'emission': emission, 'lifespan': lifespan, 'speed': speed,
                    'width': width, 'length': length, 'max_particles_est': round(emission * lifespan),
                    'animated_tracks': rec[q + 16:].count(b'KP2E') + rec[q + 16:].count(b'KP2V')})
        p += size
    return out


def main(map_path, model):
    arc = Archive(map_path)
    m = arc.read(model) or arc.read(model[:-4] + '.mdx')
    print(model, len(m), 'bytes')
    for tag, data in chunks(m):
        if tag == 'VERS':
            print('  version', struct.unpack_from('<I', data)[0])
        elif tag == 'SEQS':
            for i in range(len(data) // 132):
                name = data[i * 132:i * 132 + 80].split(b'\0')[0].decode('latin1')
                a, b = struct.unpack_from('<II', data, i * 132 + 80)
                print('  sequence %-20s %6d ~ %6d  (%d ms)' % (name, a, b, b - a))
        elif tag == 'TEXS':
            for i in range(len(data) // 268):
                path = data[i * 268 + 4:i * 268 + 264].split(b'\0')[0].decode('latin1')
                print('  texture', path or '(replaceable)', '| in map:', bool(path) and arc.find(path) is not None)
        elif tag == 'PRE2':
            for e in pre2(data):
                print('  PRE2', e)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
