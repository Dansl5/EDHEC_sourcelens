#!/usr/bin/env python3
"""Minimal QR code generator (standard library only): byte mode, error correction level M, versions 1-10.

Usage: python3 experiment/make_qr.py [URL] [OUT.png]
Defaults to the qr-hallway tracking link and experiment/qr-hallway.png.
"""
import struct
import sys
import zlib

DEFAULT_URL = "https://dansl5.github.io/EDHEC_sourcelens/?utm_source=qr-hallway&utm_medium=print&utm_campaign=hw2"

# Level M: version -> (EC codewords per block, [(block count, data codewords per block), ...])
EC_M = {
    1: (10, [(1, 16)]), 2: (16, [(1, 28)]), 3: (26, [(1, 44)]), 4: (18, [(2, 32)]),
    5: (24, [(2, 43)]), 6: (16, [(4, 27)]), 7: (18, [(4, 31)]), 8: (22, [(2, 38), (2, 39)]),
    9: (22, [(3, 36), (2, 37)]), 10: (26, [(4, 43), (1, 44)]),
}
ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38],
         8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}

# GF(256) arithmetic, primitive polynomial 0x11D
EXP = [0] * 512
LOG = [0] * 256
_x = 1
for _i in range(255):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    EXP[_i] = EXP[_i - 255]


def gf_mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]


def rs_generator(n):
    g = [1]
    for i in range(n):
        ng = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            ng[j] ^= c
            ng[j + 1] ^= gf_mul(c, EXP[i])
        g = ng
    return g


def rs_remainder(data, n):
    gen = rs_generator(n)
    rem = [0] * n
    for b in data:
        factor = b ^ rem[0]
        rem = rem[1:] + [0]
        for i in range(n):
            rem[i] ^= gf_mul(gen[i + 1], factor)
    return rem


def pick_version(nbytes):
    for v in range(1, 11):
        ec, groups = EC_M[v]
        cap = sum(c * d for c, d in groups)
        if 4 + (8 if v < 10 else 16) + 8 * nbytes <= cap * 8:
            return v
    raise ValueError("data too long for versions 1-10")


def build_codewords(data, v):
    ec, groups = EC_M[v]
    cap = sum(c * d for c, d in groups)
    bits = "0100" + format(len(data), "08b" if v < 10 else "016b") + "".join(format(b, "08b") for b in data)
    bits += "0" * min(4, cap * 8 - len(bits))
    bits += "0" * (-len(bits) % 8)
    cws = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    while len(cws) < cap:
        cws.append(pad[(len(cws) - len(bits) // 8) % 2])
    blocks, pos = [], 0
    for count, dlen in groups:
        for _ in range(count):
            blocks.append(cws[pos:pos + dlen])
            pos += dlen
    ecs = [rs_remainder(b, ec) for b in blocks]
    out = []
    for i in range(max(len(b) for b in blocks)):
        for b in blocks:
            if i < len(b):
                out.append(b[i])
    for i in range(ec):
        for e in ecs:
            out.append(e[i])
    return out


def bch(value, poly, total_bits, data_bits):
    v = value << (total_bits - data_bits)
    for i in range(data_bits - 1, -1, -1):
        if v >> (i + total_bits - data_bits) & 1:
            v ^= poly << i
    return (value << (total_bits - data_bits)) | v


def make_matrix(data, v, mask):
    n = 17 + 4 * v
    M = [[None] * n for _ in range(n)]
    fn = [[False] * n for _ in range(n)]  # function-pattern modules

    def put(r, c, val):
        M[r][c] = val
        fn[r][c] = True

    def finder(r0, c0):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                r, c = r0 + dr, c0 + dc
                if 0 <= r < n and 0 <= c < n:
                    inside = 0 <= dr <= 6 and 0 <= dc <= 6
                    dark = inside and (dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4))
                    put(r, c, dark)

    finder(0, 0); finder(0, n - 7); finder(n - 7, 0)
    pos = ALIGN[v]
    for r in pos:
        for c in pos:
            if (r <= 8 and c <= 8) or (r <= 8 and c >= n - 9) or (r >= n - 9 and c <= 8):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    put(r + dr, c + dc, max(abs(dr), abs(dc)) != 1)
    for i in range(8, n - 8):
        put(6, i, i % 2 == 0)
        put(i, 6, i % 2 == 0)
    put(n - 8, 8, True)  # dark module
    # reserve format areas
    for i in range(9):
        for (r, c) in ((8, i), (i, 8)):
            if not fn[r][c]:
                put(r, c, False)
    for i in range(8):
        put(8, n - 1 - i, False)
        put(n - 1 - i, 8, False)
    put(n - 8, 8, True)
    if v >= 7:
        for i in range(18):
            a, b = n - 11 + i % 3, i // 3
            put(a, b, False)
            put(b, a, False)
    # place data
    cws = build_codewords(data, v)
    bits = "".join(format(c, "08b") for c in cws)
    bits += "0" * (7 if 2 <= v <= 6 else 0)
    idx = 0
    c = n - 1
    up = True
    while c > 0:
        if c == 6:
            c -= 1
        rng = range(n - 1, -1, -1) if up else range(n)
        for r in rng:
            for cc in (c, c - 1):
                if not fn[r][cc]:
                    bit = idx < len(bits) and bits[idx] == "1"
                    idx += 1
                    inv = [lambda r, c: (r + c) % 2 == 0, lambda r, c: r % 2 == 0, lambda r, c: c % 3 == 0,
                           lambda r, c: (r + c) % 3 == 0, lambda r, c: (r // 2 + c // 3) % 2 == 0,
                           lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
                           lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
                           lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0][mask](r, cc)
                    M[r][cc] = bit != inv
        up = not up
        c -= 2
    # format info (level M = 00)
    fmt = bch((0b00 << 3) | mask, 0x537, 15, 5) ^ 0x5412
    for i in range(15):
        bit = bool(fmt >> i & 1)
        # first copy
        if i < 6: M[i][8] = bit
        elif i < 8: M[i + 1][8] = bit
        elif i == 8: M[8][7] = bit
        else: M[8][14 - i] = bit
        # second copy
        if i < 8: M[8][n - 1 - i] = bit
        else: M[n - 15 + i][8] = bit
    M[n - 8][8] = True
    if v >= 7:
        vi = bch(v, 0x1F25, 18, 6)
        for i in range(18):
            bit = bool(vi >> i & 1)
            M[n - 11 + i % 3][i // 3] = bit
            M[i // 3][n - 11 + i % 3] = bit
    return M


def penalty(M):
    n = len(M)
    p = 0
    for grid in (M, [list(r) for r in zip(*M)]):
        for row in grid:
            run, prev = 1, row[0]
            for x in row[1:]:
                if x == prev:
                    run += 1
                else:
                    if run >= 5: p += run - 2
                    run, prev = 1, x
            if run >= 5: p += run - 2
            s = "".join("1" if x else "0" for x in row)
            p += 40 * (s.count("10111010000") + s.count("00001011101"))
    for r in range(n - 1):
        for c in range(n - 1):
            if M[r][c] == M[r][c + 1] == M[r + 1][c] == M[r + 1][c + 1]:
                p += 3
    dark = sum(sum(1 for x in row if x) for row in M)
    p += 10 * (abs(dark * 100 // (n * n) - 50) // 5)
    return p


def qr(text):
    data = text.encode("utf-8")
    v = pick_version(len(data))
    best = min((make_matrix(data, v, m) for m in range(8)), key=penalty)
    return best


def write_png(M, path, scale=10, quiet=4):
    n = len(M)
    size = (n + 2 * quiet) * scale
    rows = []
    for r in range(-quiet, n + quiet):
        line = bytearray()
        for c in range(-quiet, n + quiet):
            dark = 0 <= r < n and 0 <= c < n and M[r][c]
            line += (b"\x00" if dark else b"\xff") * scale
        rows.extend([b"\x00" + bytes(line)] * scale)
    raw = b"".join(rows)

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 0, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    out = sys.argv[2] if len(sys.argv) > 2 else "experiment/qr-hallway.png"
    write_png(qr(url), out)
    print("wrote", out, "for", url)
