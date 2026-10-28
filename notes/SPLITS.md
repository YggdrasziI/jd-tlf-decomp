# Splits

What the build proves: the all-assembly build (splat) reproduces the bytes of each
region. It does not prove any translation-unit boundary; a boundary is proven only
when the unit is decompiled and matches.

## Region map of LEVELSTARTUP_DISC.PRX (vram)

| Range | splat subsegment | Content |
|---|---|---|
| 0x000000-0x08EBB4 | `text` (asm) | `.text`, not split yet |
| 0x08EBB4-0x08EC08 | `unit_0008EBB4` (cpp) | see Units |
| 0x08EC08-0x0960A4 | `text_0008EC08` (asm) | `.text`, not split yet |
| 0x0960A4-0x09630C | `unit_000960A4` (cpp) | see Units |
| 0x09630C-0x0964A4 | `text_0009630C` (asm) | `func_0009630C`, part of `unit_000960A4`, not matching yet |
| 0x0964A4-0x096528 | `unit_000960A4_1` (cpp) | second part of `unit_000960A4` |
| 0x096528-0x09B834 | `text_00096528` (asm) | `.text`, not split yet |
| 0x09B834-0x09B874 | `unit_0009B834` (cpp) | see Units |
| 0x09B874-0x10B5E4 | `text_0009B874` (asm) | `.text`, not split yet |
| 0x10B5E4-0x10B964 | `scestub` (asm) | system import stubs (`.sceStub.text.*`) |
| 0x10B964-0x10BABC | `sceresident` (rodata) | `.rodata.sceResident`: library names, export NIDs and values |
| 0x10BABC-0x10BC50 | `lib` (rodata) | `.lib.ent*`, `.lib.stub*`, `.rodata.sceModuleInfo` |
| 0x10BC50-0x10BF80 | `scenid` (rodata) | `.rodata.sceNid` |
| 0x10BF80-0x116100 | `rodata` (rodata) | `.rodata` (+ padding to 0x116100) |
| 0x116100-0x12B160 | `data` (data) | `.data` |
| 0x12B160-0x12B168 | `unit_0008EBB4` (`.data`) | data of the unit |
| 0x12B168-0x12CA90 | `data_0012B168` (data) | `.data` |
| 0x12CA90-0x12CA98 | `unit_0009B834` (`.data`) | data of the unit |
| 0x12CA98-0x13FCF8 | `data_0012CA98` (data) | `.data` |
| 0x13FCF8-0x13FD6C | `eh_frame` (data) | `.eh_frame` |
| 0x13FD6C-0x14004C | `mcpstub` (data) | `.sceStub.text.mcp` (92 stubs) |
| 0x14004C-0x1408A4 | `ctors` (data) | `.ctors`, `.dtors`, `.cplinit`, `.psp_lib_markimport_`, `.psp_lib_mark_`, `.linkonce.d` |
| 0x1408A8-0x1408C0 | `sdata` (data) | `.sdata` (program header 1) |
| 0x1408C0-0x1D9970 | `bss` | `.sbss`, `.bss` |

## Code regions of `.text` (vram)

How each bound was found; "hypothesis" means not proven by a matching unit.

| Range | Content | Evidence |
|---|---|---|
| 0x000000-0x0F16AC | game and engine code (C++) | the 87 first `.cplinit` entries (unit ends, below); calls to the 92 `mcp` imports (functions of the EBOOT) all over it; source paths `ENGINE/` and `SHARED/WAD/` (below); the code after 0x0F16AC calls back into it only through the start-up code (0x0F1B34 calls 0x014CAC, hypothesis: the game main) and from 0x10721C on |
| 0x0F16AC-0x0F1EC0 | C library start-up and system glue (hypothesis: SDK libc / crt0) | `_exit`, `libc:%s: should be called from main thread` (0x0F16AC); sbrk on `UserSbrkLow`/`UserSbrkHigh` (0x0F17BC, `sceKernelAllocPartitionMemory`); stdin/stdout/stderr handles (0x0F18D4); `module_start` (0x0F197C, export table, starts the `user_main` thread) and `module_stop` (0x0F1B04) |
| 0x0F1EC0-0x0F4394 | C++ runtime (hypothesis: SNC runtime) | `bad_alloc` (0x0F1EC0); `C++ runtime abort`, `terminate() called by the exception handling mechanism` (0x0F1F94); 0x0F1ED8 called by every deleting destructor of the module (hypothesis: `operator delete`); 0x0F36E8 called by 18 static initializers (hypothesis: `__record_needed_destruction`, named by the SNC probe) |
| 0x0F4394-0x0F5460 | single-precision math library | error names `acosf`, `asinf`, `atan2f`, `expf`, `fmodf`, `powf`, `sqrtf`, one per function |
| 0x0F5460-0x104530 | C library: formatted output, locale, arithmetic helpers (hypothesis: SDK libc) | `-Inf`/`Inf`/`NaN` (0x0FC450); `(null)`, `0123456789abcdef` (0x0FCDFC, 0x0FE79C: printf family); `sceKernelCpuSuspendIntr`/`ResumeIntr` (0x100C24); `C-SJIS`, `C-EUCJP`, `C-JIS` (0x101ED4); no call into the game region |
| 0x104530-0x10721C | GE graphics library, C++ | first `sceGe*` import calls at 0x104530 (`sceGeEdramGetAddr`, `sceGeSetCallback`), then `sceGeListEnQueue`, `sceGeListUpdateStallAddr`, `sceDisplaySetFrameBuf`...; functions writing GE command words (`0x106140`: `0xD0000000 | float >> 8`); ends with the last `.cplinit` entry 0x1068F0-0x10721C (fills a table of GE commands): one SNC-compiled file at least |
| 0x10721C-0x10B5E4 | functions called from the game, after the libraries | hypothesis: inline and template copies (COMDAT) the linker placed last: repeated shapes (recursive tree walks 0x1085A4/0x1095A8, 16 deleting destructors of 0x48 bytes calling 0x0F1ED8 at 0x109F80-0x10A3B8), many reached only through pointers; to check against the linker's COMDAT placement |

Library code after the game code is the usual link order (objects, then
libraries). Within 0x0F16AC-0x10721C, sub-ranges are taken from the first function
showing each string or import; their inner bounds are approximate.

## Unit ends from `.cplinit`

SNC emits the static initialization of a file (`__sti__<file>`) after all its
other functions and lists it in `.cplinit` (`tools/probes/snc_sti.cpp`,
`notes/COMPILER.md`). The PRX `.cplinit` holds 88 such functions, in increasing
address order (= link order): each ends the own code of one source file.
`python tools/tu_ends.py` lists them with the unit end. Files without global
objects to construct have no entry, so two entries can enclose several files.

- 87 entries in the game region, from 0x0007D8 to 0x0EA214; the densest stretch is
  0x070000-0x0A62A4 (56 entries).
- No entry between 0x0A62A4 (end of the entry 0x0A5D9C) and 0x0BC580: the code there has no
  static objects, its file bounds must come from other evidence.
- `unit_000960A4` starts at 0x0960A4, right after the end of the entry 0x096058:
  consistent with a file starting there.

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

| `src/unit_0008EBB4.cpp` | 0x08EBB4-0x08EC08, data 0x12B160-0x12B168 | `func_0008EBB4`, `func_0008EBBC` (calls `func_0007E918`), `func_0008EBD8`, `func_0008EBE0` (passed together as callbacks by `func_0007FF08`), static initialization 0x8EBE8 (`D_0012B164 = D_0012B160 * 0.5f`) | matching, data included (2026-10-28) | **proven at both ends** (`.cplinit` entries 0x8EA44 and 0x8EBE8); same data and initialization as `unit_0009B834` (hypothesis: shared header) |
| `src/unit_0009B834.cpp` | 0x09B834-0x09B874, data 0x12CA90-0x12CA98 | `func_0009B834`, `func_0009B83C`, `func_0009B844`, `func_0009B84C` (empty; passed together as callbacks by `func_0007FAF8`), static initialization 0x9B854 (`D_0012CA94 = D_0012CA90 * 0.5f`) | matching, data included (2026-10-28) | **proven at both ends**: the previous `.cplinit` entry ends at 0x9B834, this file's entry 0x9B854 ends it; its `.data` (the two floats, 8 bytes, 8-aligned) is the SNC layout of the source |

An `asm` piece is named after its start vram (`text_00096528`); file offset = vram +
0x74.
