# Splits

What the build proves: the all-assembly build (splat) reproduces the bytes of each
region. It does not prove any translation-unit boundary; a boundary is proven only
when the unit is decompiled and matches.

## Region map of LEVELSTARTUP_DISC.PRX (vram)

| Range | splat subsegment | Content |
|---|---|---|
| 0x000000-0x10B5E4 | `text` (asm) | `.text`, every function; units not split yet |
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

None yet.
