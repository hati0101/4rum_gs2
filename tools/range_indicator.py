"""Build an isolated GSRI preview map and a source-derived coverage report.

python tools/range_indicator.py INPUT.w3x OUTPUT.w3x --game "D:\\Warcraft III"
Never overwrites an input/output map. No changes to original ability data.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

from casc import Casc
from objdata import load_objects, load_strings, resolve
from w3x import Archive, encrypt, hash_string, FLAG_EXISTS, FLAG_COMPRESS

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'A0OB': '디멘션 도어', 'A0T1': '데스 프로마이즈',
           'A11L': '카오스 위치: 타임 오브 데스', 'A07I': '에인션트 트리(윗브): 네추럴링'}
# Targeted native families. Zero/unlimited ranges are filtered at runtime too.
TARGETED = set('''ACbf ACbz ACca ACs7 ACst ACtb ACuf AEbl AEer AEmb AEsh
AHbn AHbz AHfa AHfs AHhb AHmt AHtb ANab ANbf ANbl ANcf ANcr ANdh ANdo
ANdr ANfl ANht ANhx ANmr ANrc ANrf ANsi ANso ANsy AOcl AOeq AOfs AOs2
AOws AUcs AUdc AUfn AUfu AUin AUsl Ablo Acri Acrs Acyc Adis Advm Aens
Aeye Afae Afla Afod Afzy Ahea Ahwd Ainf Aivs Alsh Amls Arai Arej Arsw
Aspl Asta Auhf Scri AItb AIsa AImt AIpg AIrl APh3 APsa'''.split())
SELF_PASSIVE = set('''ACmo AEfk AEfn AEim AEme AEpa AEsf AEtq AHab AHds AHtc
AHwe AIpv ANdp ANef ANic ANms ANrg ANwk AOmi AOsf AOw2 AOwk AOww AUan
AUau AUls AUts Aakb Aamk Abrf Absk Aclf Acn2 Adef Aeat Aesr Amfl Aroa
Awrh Awrs SCae'''.split())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stock_data(game):
    c = Casc(str(game))
    entries = dict(line.split('|')[:2] for line in c.root().decode().splitlines() if '|' in line)
    key = next(v for k, v in entries.items() if k.lower() == 'war3.w3mod:units/abilitydata.slk')
    rows, y = {}, 0
    for line in c.read_ckey(bytes.fromhex(key)).decode().splitlines():
        if line.startswith('C;'):
            fields = dict((s[0], s[1:]) for s in line.split(';')[1:] if s)
            y = int(fields.get('Y', y))
            rows.setdefault(y, {})[int(fields['X'])] = fields.get('K', '').strip('"')
    hdr = rows.pop(1)
    mapped = [{hdr[x]: v for x, v in r.items()} for r in rows.values()]
    return {r['alias']: r for r in mapped if 'alias' in r}, c.version


def function_text(script, name):
    m = re.search(r'^function '+re.escape(name)+r'\b.*?^endfunction', script, re.M | re.S)
    if not m:
        raise ValueError('missing audited function: '+name)
    return m.group()


def catalog(arc, stock):
    objs = load_objects(arc, 'war3map.w3a')
    skin = load_objects(arc, 'war3mapSkin.w3a')
    strings = load_strings(arc)
    script = arc.read('war3map.j').decode('utf-8')
    panel = function_text(script, 'GSTF_SkillOf')
    panel_ids = set(re.findall(r"return '(.{4})'", panel))
    added = set(re.findall(r"UnitAddAbility(?:BJ)?\(\s*'(.{4})'", script))
    added |= set(re.findall(r"UnitAddAbility\([^,\n]+,\s*'(.{4})'", script))
    rows = []
    for aid in sorted(set(objs) | set(skin)):
        o = objs.get(aid, {}) | skin.get(aid, {})
        base = o.get('base', aid)
        default = stock.get(base, {})
        name = str(resolve(o.get('atp11', o.get('anam', aid)), strings))
        key = str(resolve(o.get('ahky', ''), strings)).upper().strip()
        owner = str(resolve(o.get('anam', ''), strings))
        if not any(hero in owner for hero in ('레인저','스펠 인보커')):
            continue
        if aid == 'A08H' and not key:
            key = 'E'  # GSTF_SkillOf Hkal slot 2; stock silence hotkey.
        levels = int(o.get('alev', default.get('levels', 1)))
        ranges = [float(o.get('aran'+str(lv), (default.get('Rng'+str(min(lv,4)), 0) if default.get('Rng'+str(min(lv,4)), 0) != '-' else 0)) or 0) for lv in range(1, levels+1)]
        kind, reason = 0, 'no_hotkey'
        if aid in EXCLUDE:
            reason = 'explicit_unlimited_exclusion'
        elif len(key) != 1 or not ('A' <= key <= 'Z'):
            pass
        elif base == 'ANcl':
            types = [int(o.get('Ncl2'+str(lv), default.get('DataB'+str(min(lv,4)), 0)) or 0) for lv in range(1, levels+1)]
            if any(t in (1,2,3) for t in types):
                kind, reason = 2, 'channel_targeted'
            else:
                reason = 'immediate_channel'
        elif base in SELF_PASSIVE:
            reason = 'self_or_passive'
        elif base in TARGETED:
            kind, reason = 1, 'targeted_native'
        else:
            reason = 'review_unknown_base'
        if kind and not any(0 < r < 9999 for r in ranges):
            kind, reason = 0, 'zero_or_unlimited_range'
        # Native non-damaging carriers can implement entirely different shapes.
        profile = 0
        if kind and aid == 'A0O8':
            profile = 2
        if kind and aid == 'A08G':
            profile = 1
        if aid in panel_ids or key or '[특성' in owner:
            rows.append(dict(id=aid, base=base, key=key, name=re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',name),
                             owner=owner, panel=aid in panel_ids, added_by_script=aid in added,
                             ranges=ranges, kind=kind, status=reason, profile=profile))
    return rows


def generate_table(rows):
    lines = ['function GSRI_LoadData takes nothing returns nothing']
    for row in rows:
        if row['kind']:
            aid = row['id']
            lines += [f"    call SaveInteger(GSRI_Data, '{aid}', 0, {ord(row['key'])})",
                      f"    call SaveInteger(GSRI_Data, '{aid}', 1, {row['kind']})"]
            if row['profile']:
                lines += [f"    call SaveInteger(GSRI_Data, '{aid}', 2, {row['profile']})"]
    lines += ['endfunction']
    return '\n'.join(lines)


def patch_j(script, code):
    if 'function GSRI_Init ' in script:
        raise ValueError('GSRI already installed; use the clean source map')
    g = re.search(r'(?m)^globals\n(.*?)^endglobals\n', code, re.S)
    declarations = g.group(1)
    functions = code[:g.start()] + code[g.end():]
    eol = '\r\n' if '\r\n' in script else '\n'
    script = script.replace('endglobals', declarations.replace('\n',eol)+'endglobals',1)
    m = re.search(r'^function main takes nothing returns nothing', script, re.M)
    assert m, 'main missing'
    script = script[:m.start()] + functions.replace('\n',eol) + eol + script[m.start():]
    m = re.search(r'^function main takes nothing returns nothing.*?^endfunction',script,re.M|re.S)
    pos = m.end()-len('endfunction')
    return script[:pos]+'    call GSRI_Init()'+eol+script[pos:]


def patch_wct(wct, code):
    if struct.unpack_from('<II',wct) != (0x80000004,1):
        raise ValueError('unsupported wct version')
    p = wct.index(b'\0',8)+1
    n = struct.unpack_from('<I',wct,p)[0]
    head = wct[p+4:p+4+n]
    if b'GSRI_Init' in head:
        raise ValueError('GSRI already in editor header')
    # JassHelper moves the globals and preserves the initializer on editor saves.
    block = ('\r\n\r\nlibrary GSRangeIndicator initializer GSRI_Init\r\n'+code.replace('\n','\r\n')+'\r\nendlibrary\r\n').encode()
    updated = head.rstrip(b'\0')+block+b'\0'
    return wct[:p]+struct.pack('<I',len(updated))+updated+wct[p+4+n:]


def write_archive(arc, destination, files):
    """Append files and tables; keep all existing compressed sectors untouched.

    This map has v100 CRC-only attributes. Other flags fail closed instead of
    writing incomplete FILETIME/MD5 tables. Existing archive writer unchanged.
    """
    buf = bytearray(arc.data)
    bt = [list(b) for b in arc.block_table]
    ht = [list(h) for h in arc.hash_table]
    files = dict(files)
    # Preserve the existing PKWARE-compressed listfile verbatim. New paths are
    # explicitly registered in war3map.imp and the output manifest.
    index = {name: arc.find(name) for name in files}
    for name in files:
        if index[name] is None:
            bi = len(bt)
            bt.append([0,0,0,0])
            index[name] = bi
            start = hash_string(name,0) % len(ht)
            for k in range(len(ht)):
                pos = (start+k) % len(ht)
                if ht[pos][4] in (0xffffffff,0xfffffffe):
                    ht[pos] = [hash_string(name,1),hash_string(name,2),0,0,bi]
                    break
            else:
                raise ValueError('MPQ hash table full')
    attrs = arc.read('(attributes)')
    if attrs:
        if struct.unpack_from('<II',attrs) != (100,1):
            raise ValueError('only CRC-only attributes supported')
        attr = bytearray(attrs)
        if len(attr) != 8+len(arc.block_table)*4:
            raise ValueError('invalid CRC table')
        attr.extend(bytes((len(bt)-len(arc.block_table))*4))
        for name,data in files.items():
            struct.pack_into('<I',attr,8+4*index[name],zlib.crc32(data)&0xffffffff)
        files['(attributes)'] = bytes(attr)
        index['(attributes)'] = arc.find('(attributes)')
    for name,data in files.items():
        blob = arc._pack(data)
        bt[index[name]] = [len(buf)-arc.base,len(blob),len(data),FLAG_EXISTS|FLAG_COMPRESS]
        buf += blob
    ht_off = len(buf)-arc.base
    buf += encrypt(b''.join(struct.pack('<IIHHI',*h) for h in ht),hash_string('(hash table)',3))
    bt_off = len(buf)-arc.base
    buf += encrypt(b''.join(struct.pack('<IIII',*b) for b in bt),hash_string('(block table)',3))
    struct.pack_into('<I',buf,arc.base+8,len(buf)-arc.base)
    struct.pack_into('<IIII',buf,arc.base+16,ht_off,bt_off,len(ht),len(bt))
    Path(destination).write_bytes(buf)
    return files


def import_entries(data, names):
    names = [n for n in names if n.lower().encode()+b'\0' not in data.lower()]
    version,count = struct.unpack_from('<II',data)
    if version != 1:
        raise ValueError('unsupported import format')
    return struct.pack('<II',version,count+len(names))+data[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in names)


def range_lightning(arc):
    # Preserve every existing row and its original encoding. Add one new ID.
    original = arc.read('Splats\\LightningData.slk')
    if not original:
        raise ValueError('Missing map LightningData.slk; review before porting')
    s = original.decode('latin1')
    if 'K"GSRL"' in s:
        raise ValueError('GSRL lightning ID already exists')
    bound = re.search(r'(?m)^B;Y(\d+);X14;D0 0 (\d+) 13',s)
    if not bound:
        raise ValueError('Unexpected lightning table bounds')
    row = int(bound[1])+1
    s = s[:bound.start()]+f'B;Y{row};X14;D0 0 {row-1} 13'+s[bound.end():]
    values = ['"GSRL"','"GSRI range line"','"GSRI"','"white.tga"',32,3,255,255,255,255,0,1,1000000,0]
    extra = '\r\n'.join(f'C;Y{row};X{i};K{v}' for i,v in enumerate(values,1))+'\r\n'
    end = re.search(r'(?m)^E\s*\Z',s)
    if not end:
        raise ValueError('Missing lightning table terminator')
    return (s[:end.start()]+extra+s[end.start():]).encode('latin1')


def build(source, destination, game):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or destination.exists():
        raise ValueError('use a new output filename; overwriting is disabled')
    arc = Archive(source)
    stock,version = stock_data(game)
    rows = catalog(arc,stock)
    # Baked geometry must never silently survive changed object dimensions.
    objects = load_objects(arc, 'war3map.w3a')
    skins = load_objects(arc, 'war3mapSkin.w3a')
    cone = objects.get('A08G', {}) | skins.get('A08G', {})
    defaults = stock[cone['base']]
    for lv in range(1, 5):
        for field, fallback, expected in [('aare', 'Area', 125 if lv == 1 else 150),
                                           ('Ucs3', 'DataC', 825), ('Ucs4', 'DataD', 200)]:
            actual = float(cone.get(field+str(lv), defaults.get(fallback+str(lv), 0)))
            if actual != expected:
                raise ValueError(f'None Q geometry changed: {field} level {lv}: {actual}; review assets')
    script = arc.read('war3map.j').decode('utf-8')
    profile_names = ['Trig_Poison_Sniping_Actions','Trig_Poison_Sniping_Move_Actions',
                     'Trig_Poison_Sniping_Move_Func001C','GS2_AuditRangeRegister']
    signatures = {n:sha(function_text(script,n).replace('\r\n','\n').encode()) for n in profile_names}
    audited = ROOT/'src/range-audited-functions.json'
    expected = json.loads(audited.read_text(encoding='utf-8'))
    mismatched = [n for n in signatures if signatures[n] != expected[n]]
    if mismatched:
        raise ValueError('Custom projectile code changed; review before porting: '+', '.join(mismatched))
    code = (ROOT/'src/RangeIndicator.template.j').read_text(encoding='utf-8').replace('//@@GSRI_TABLE@@',generate_table(rows))
    (ROOT/'src/RangeIndicator.j').write_text(code,encoding='utf-8',newline='\n')
    files = {'war3map.j':patch_j(script,code).encode('utf-8'), 'war3map.wct':patch_wct(arc.read('war3map.wct'),code)}
    assets = {'GSRI\\white.tga':(ROOT/'assets/range/white.tga').read_bytes(),
              'Splats\\LightningData.slk':range_lightning(arc)}
    files.update(assets)
    files['war3map.imp'] = import_entries(arc.read('war3map.imp'),list(assets))
    destination.parent.mkdir(parents=True,exist_ok=True)
    changed = write_archive(arc,destination,files)
    result = Archive(destination)
    for name,data in changed.items():
        assert result.read(name) == data, 'readback mismatch: '+name
    preserved = 0
    # Compare every original compressed block, including unknown filenames and
    # compression formats. Unchanged blocks must retain metadata and raw bytes.
    replaced_indices = {arc.find(n) for n in changed if n in arc}
    for i, block in enumerate(arc.block_table):
        if i not in replaced_indices:
            assert result.block_table[i] == block, 'unexpected block change: '+str(i)
            off, size, _, _ = block
            assert result.data[result.base+off:result.base+off+size] == arc.data[arc.base+off:arc.base+off+size]
            preserved += 1
    assert source.read_bytes() == arc.data, 'input map changed'
    report = destination.with_suffix('.coverage.csv')
    with report.open('w',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    manifest = dict(status='PREPARED_NOT_PUBLISHED_RUNTIME_UNVERIFIED',source=str(source),
                    source_sha256=sha(arc.data),output=destination.name,output_sha256=sha(destination.read_bytes()),
                    game_version=version,enabled_heroes=['Hvwd (Ranger / Earthlake)','Hkal (Spell Invoker / None)'],changed_members=sorted(changed),preserved_members=preserved,
                    statuses=dict(collections.Counter(r['status'] for r in rows)),
                    supported=sum(bool(r['kind']) for r in rows),
                    profiles=[r['id'] for r in rows if r['profile']],
                    explicit_exclusions=EXCLUDE,custom_function_signatures=signatures)
    destination.with_suffix('.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('destination');p.add_argument('--game',required=True)
    args=p.parse_args()
    build(args.source,args.destination,args.game)
