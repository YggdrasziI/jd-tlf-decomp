#!/usr/bin/env python3
"""Compile a C/C++ probe and compare each function whose name contains
`func_XXXXXXXX` with the original PRX at that vram, relocated fields masked.

usage: compiler_probe.py <src> [--cc <compiler>] [-- compiler flags...]
"""

import argparse
import re
import struct
import subprocess
import sys
from pathlib import Path

from prx import Prx

PRX = Path("orig/NPUG80330/LEVELSTARTUP_DISC.PRX")
OBJDUMP = Path("tools/binutils/mips-ps2-decompals-objdump.exe")
SNC = Path("tools/compilers/pspsnc_1.2.7503.0/pspsnc.exe")


def disassemble(obj: Path) -> dict[int, list[tuple[int, int]]]:
    """Return {vram: [(word, compare mask), ...]} for the probe's func_ symbols."""
    dump = subprocess.run([str(OBJDUMP.resolve()), "-dr", str(obj)],
                          capture_output=True, text=True, check=True).stdout
    funcs: dict[int, list[list[int]]] = {}
    cur = None
    for line in dump.splitlines():
        if m := re.match(r"^[0-9a-f]+ <(.*)>:", line):
            a = re.search(r"func_([0-9A-F]{8})", m.group(1))
            cur = funcs.setdefault(int(a.group(1), 16), []) if a else None
        elif cur is None:
            continue
        elif m := re.match(r"^\s+[0-9a-f]+:\s+([0-9a-f]{8})\s", line):
            cur.append([int(m.group(1), 16), 0xFFFFFFFF])
        elif (m := re.match(r"^\s+[0-9a-f]+: (R_MIPS_\w+)", line)) and cur:
            cur[-1][1] = 0xFC000000 if m.group(1) == "R_MIPS_26" else 0xFFFF0000
    return {a: [tuple(i) for i in insns] for a, insns in funcs.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("src", type=Path)
    parser.add_argument("--cc", type=Path, default=SNC)
    parser.add_argument("flags", nargs="*")
    args = parser.parse_args()

    obj = args.src.with_suffix(".o")
    r = subprocess.run([str(args.cc.resolve()), "-c", *args.flags, "-o", str(obj), str(args.src)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)

    prx = Prx(PRX)
    text_offset = prx.segments[0].offset
    matched = 0
    funcs = disassemble(obj)
    for addr, insns in sorted(funcs.items()):
        bad = [i for i, (word, mask) in enumerate(insns)
               if (struct.unpack_from("<I", prx.data, text_offset + addr + 4 * i)[0] ^ word) & mask]
        matched += not bad
        state = "OK" if not bad else "DIFF at insn " + ",".join(map(str, bad))
        print(f"func_{addr:08X}: {state} ({len(insns)} insns)")
    print(f"{matched}/{len(funcs)} match")


if __name__ == "__main__":
    main()
