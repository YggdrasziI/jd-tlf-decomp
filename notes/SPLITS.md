# Splits

What the build proves: the all-assembly build (splat) reproduces the bytes of each
region. It does not prove any translation-unit boundary; a boundary is proven only
when the unit is decompiled and matches.

## Region map of LEVELSTARTUP_DISC.PRX (vram)

| Range | splat subsegment | Content |
|---|---|---|
| 0x000000-0x0960A4 | `text` (asm) | `.text`, not split yet |
| 0x0960A4-0x09630C | `unit_000960A4` (cpp) | see Units |
| 0x09630C-0x0964A4 | `text_0009630C` (asm) | `func_0009630C`, part of `unit_000960A4`, not matching yet |
| 0x0964A4-0x096528 | `unit_000960A4_1` (cpp) | second part of `unit_000960A4` |
| 0x096528-0x10B5E4 | `text_00096528` (asm) | `.text`, not split yet |
| 0x10B5E4-0x10B964 | `scestub` (asm) | system import stubs (`.sceStub.text.*`) |
| 0x10B964-0x10BABC | `sceresident` (rodata) | `.rodata.sceResident`: library names, export NIDs and values |
| 0x10BABC-0x10BC50 | `lib` (rodata) | `.lib.ent*`, `.lib.stub*`, `.rodata.sceModuleInfo` |
| 0x10BC50-0x10BF80 | `scenid` (rodata) | `.rodata.sceNid` |
| 0x10BF80-0x116100 | `rodata` (rodata) | `.rodata` (+ padding to 0x116100) |
| 0x116100-0x13FCF8 | `data` (data) | `.data` |
| 0x13FCF8-0x13FD6C | `eh_frame` (data) | `.eh_frame` |
| 0x13FD6C-0x14004C | `mcpstub` (data) | `.sceStub.text.mcp` (92 stubs) |
| 0x14004C-0x1408A4 | `ctors` (data) | `.ctors`, `.dtors`, `.cplinit`, `.psp_lib_markimport_`, `.psp_lib_mark_`, `.linkonce.d` |
| 0x1408A8-0x1408C0 | `sdata` (data) | `.sdata` (program header 1) |
| 0x1408C0-0x1D9970 | `bss` | `.sbss`, `.bss` |

## Source paths found in strings

Each is a lead for a unit name and bound (SPEC.md naming), not a bound:

| String address | Path |
|---|---|
| 0x10DC08 | `v:/PROJECTS/JAK1/CODE/ENGINE/video.cpp` |
| 0x10EB50 | `v:/PROJECTS/JAK1/CODE/ENGINE/PSP/PSPTextureManager.cpp` |
| 0x10EDC4 | `v:/PROJECTS/JAK1/CODE/ENGINE/PSP/PSPDraw.cpp` |
| 0x110E18 | `v:/PROJECTS/JAK1/CODE/SHARED/WAD/loader.cpp` |
| 0x110E80 | `v:/PROJECTS/JAK1/CODE/SHARED/WAD/loadCharacter.cpp` |

## Units

| Unit | vram range | Functions | Status | Bounds |
|---|---|---|---|---|
| `src/unit_000960A4.cpp` + `src/unit_000960A4_1.cpp` | 0x0960A4-0x096528 | `func_000960A4` (get `D_0012C280`), `func_000960B0` (`D_0012C280 == -1`), `func_000960C4` (set `D_0012BFE8`), `func_000960D0`/`func_00096160` (next/previous index in 0-5 where `func_000BC22C` returns 3), `func_000961E8` (applies the selection `D_0012C01C`), `func_0009630C` (assembly), `func_000964A4` (fills a selection) | 7 / 8 matching (2026-10-28); `func_0009630C` stays assembly (register allocation of the second owner test and the loop counters) | hypothesis: one file, since all eight use `D_0012C280` or the selection; the unit is split in two `.cpp` around the unfinished function |

An `asm` piece is named after its start vram (`text_00096528`); file offset = vram +
0x74.
