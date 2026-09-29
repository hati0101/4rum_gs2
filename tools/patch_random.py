"""Patch the "Random Hero" custom-text trigger (-랜덤) in war3map.wct and war3map.j.

1. Can be run from the hero board's random button: the board stores the player id
   in the hidden frame GSPF_RandPid and calls ExecuteFunc("Trig_random_Actions");
   with no triggering player the trigger reads that id. (Chat use is unchanged.)
   All other GetTriggerPlayer() calls in the function use RandPlayer.
2. Without All Pick, Darkness players always roll from the Darkness range
   (before: the +HeroMax[1] offset was skipped when the Guardian hero with the
   same number was on the map, giving a Darkness player a Guardian hero).
3. Heroes already on the map (e.g. bought from a shop) are skipped, not only
   heroes marked in udg_RandHero (randomed/banned).
4. Gives up after 500 rolls instead of looping forever.
Gold is unchanged: -랜덤 costs no gold (shop purchase costs 200).

usage: python patch_random.py <input.w3x> <output.w3x>
"""
import struct
import sys

from w3x import Archive

FUNC = 'function Trig_random_Actions takes nothing returns nothing'

EDITS = [
    ('local integer i = 0\n',
     'local integer i = 0\n'
     'local integer tries = 0\n'
     '\n'
     '// 영웅 선택판 랜덤 버튼(ExecuteFunc)으로 불리면 이벤트 플레이어가 없음 -> 선택판이 저장한 플레이어 번호\n'
     'if (RandPlayer == null) then\n'
     'set RandPlayer = Player(S2I(BlzFrameGetText(BlzGetFrameByName("GSPF_RandPid", 0))))\n'
     'endif\n'),
    ('if ( CountUnitsInGroup(GetUnitsOfTypeIdAll( udg_Hero[RandHero] )) == 0 ) and (udg_ModeAllpick == false) and (IsPlayerAlly(RandPlayer,udg_Force[2])) then\n'
     'set RandHero = RandHero+udg_HeroMax[1]\n'
     'endif\n'
     '\n'
     'if (udg_RandHero[RandHero] == false) then\n',
     '// 올픽이 아니면 다크니스는 항상 다크니스 영웅 범위\n'
     'if (udg_ModeAllpick == false) and (IsPlayerAlly(RandPlayer,udg_Force[2])) then\n'
     'set RandHero = RandHero+udg_HeroMax[1]\n'
     'endif\n'
     '\n'
     'set tries = tries + 1\n'
     'if (tries > 500) then\n'
     'call DisplayTimedTextToPlayer(RandPlayer, 0, 0, 10, "|cffff8080랜덤으로 고를 수 있는 영웅이 없습니다.|r")\n'
     'set udg_RandomRuning = false\n'
     'return\n'
     'endif\n'
     '\n'
     '// 랜덤/밴 된 영웅(udg_RandHero)과 이미 맵에 있는 영웅(상점 구매 등) 제외\n'
     'if (udg_RandHero[RandHero] == false) and (CountUnitsInGroup(GetUnitsOfTypeIdAll( udg_Hero[RandHero] )) == 0) then\n'),
]


def patch_func(text):
    """Patch the Trig_random_Actions function inside a script text (LF line endings)."""
    a = text.index(FUNC)
    b = text.index('\nendfunction', a)
    body = text[a:b]
    if 'GSPF_RandPid' in body:
        raise SystemExit('already patched')
    head, rest = body.split('\n', 2)[:2], body.split('\n', 2)[2]
    first = '\n'.join(head) + '\n'
    assert head[1].strip() == 'local player RandPlayer = GetTriggerPlayer()', head[1]
    rest = '\n'.join(l if l.lstrip().startswith('//') else l.replace('GetTriggerPlayer()', 'RandPlayer')
                     for l in rest.split('\n'))
    for old, new in EDITS:
        assert rest.count(old) == 1, old[:60]
        rest = rest.replace(old, new)
    return text[:a] + first + rest + text[b:]


def patch_script(raw):
    text = raw.decode('utf-8')
    crlf = '\r\n' in text
    text = patch_func(text.replace('\r\n', '\n'))
    return (text.replace('\n', '\r\n') if crlf else text).encode('utf-8')


def patch_wct(wct):
    """Find the length-prefixed custom text record holding the function and patch it."""
    i = wct.index(FUNC.encode())
    for q in range(i, max(4, i - 400000), -1):
        n, = struct.unpack_from('<I', wct, q - 4)
        if i - q < n <= len(wct) - q and wct[q + n - 1] == 0 and FUNC.encode() in wct[q:q + n]:
            rec = wct[q:q + n - 1]
            new = patch_script(rec) + b'\0'
            return wct[:q - 4] + struct.pack('<I', len(new)) + new + wct[q + n:]
    raise SystemExit('trigger text record not found in wct')


def main(src, dst):
    arc = Archive(src)
    arc.save_with_replacements(dst, {
        'war3map.j': patch_script(arc.read('war3map.j')),
        'war3map.wct': patch_wct(arc.read('war3map.wct')),
    })
    print('patched Trig_random_Actions (j + wct) ->', dst)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
