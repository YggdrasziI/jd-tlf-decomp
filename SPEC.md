# Jak and Daxter: The Lost Frontier (PSP) decompilation — specification

## Goal

Rebuild Jak and Daxter: The Lost Frontier (PlayStation Portable) from C/C++ source
written from scratch so that, compiled with the original compiler and flags, it
produces game modules identical byte for byte to the original files.

Out of scope: a port, game assets, any redistribution of game files.

## Target

| Item | Value | Evidence |
|---|---|---|
| Disc ID | `NPUG80330` (US), `DISC_VERSION 1.00`, `PSP_SYSTEM_VER 5.50`, publisher SCEA | `PSP_GAME/PARAM.SFO` |
| ISO SHA-1 | `70ec78b94b142fdff3072c207b13cb6cda22941e` (1453916160 bytes) | `tools/extract.py` |
| Target module | `PSP_GAME/USRDIR/BIN/LEVELSTARTUP_DISC.PRX`, 1610377 bytes, SHA-1 `c0204feebb7ba0e643b12008880da7b074b627cf` | `config/NPUG80330/build.sha1` |
| Module | name `jak1`, version 1.1, attributes 0, SDK version word `0x05050010` | `.rodata.sceModuleInfo`, `module_sdk_version` (0x10E1A0) |
| Format | unencrypted relocatable PRX (ELF type 0xFFA0, flags 0x10A23001), 2 program headers, 56 section headers, empty `.symtab` | `tools/prx_info.py` |
| Program header 0 | file 0x74, vram 0x0, 0x1408A4 bytes: `.text` 0x0-0x10B5E4 (0x10B5E4), import stubs, `.rodata` 0x10BF80-0x1160C8, `.data` 0x116100-0x13FCF5, `.eh_frame`, `.sceStub.text.mcp`, `.ctors`, `.dtors`, `.cplinit`, `.linkonce.d` | section headers |
| Program header 1 | file 0x140918, vram 0x1408A8: `.sdata` 0x18, `.sbss` 0x120, `.bss` 0x98F70; `$gp` = segment base + 0x7FF0 = 0x148898 | section headers, module info |
| Entry | `module_start` 0xF197C, `module_stop` 0xF1B04 | `.lib.ent` (standard SDK export NIDs) |
| Imports | 15 system libraries (124 functions, named from their NID) and 92 functions of `mcp`, the module in `SYSDIR/EBOOT.BIN` | `.lib.stub`, `config/NPUG80330/symbol_addrs.prx.txt` |
| Relocations | `.rel.text`: 14681 R_MIPS_26, 8109 R_MIPS_HI16, 10605 R_MIPS_LO16; data tables: R_MIPS_32. References into program header 1 are stored relative to its base | `tools/prx_info.py`, `notes/PRX.md` |
| Source language | C++ (`v:/PROJECTS/JAK1/CODE/ENGINE/video.cpp`, `.../ENGINE/PSP/PSPDraw.cpp`, `.../SHARED/WAD/loader.cpp`...) | strings in `.rodata` |

Other modules on the disc (later): `SYSDIR/EBOOT.BIN` (encrypted
`~PSP`, module `mcp`), 29 level PRX (`101BRINKTRAINING_DISC.PRX`...), `TRANSDEFAULT`
and 25 `TRANSG*` PRX. A rough comparison (2026-10-27) found about half of
LEVELSTARTUP's code blocks in other PRX: the engine is linked into every module.

## Toolchain

Evidence and the candidate analysis go in `notes/COMPILER.md`.

- splat **0.50.1** (`splat64[mips]`, spimdisasm 1.42.4, rabbitizer 1.16.2): assembly,
  data and linker script from `config/NPUG80330/splat.levelstartup.yaml`.
- binutils from [decompals/binutils-mips-ps2-decompals](https://github.com/decompals/binutils-mips-ps2-decompals)
  **v0.10** (`as -march=mips32r2 -mabi=32`, `ld`, `objcopy`), downloaded by `ninja`
  into `tools/binutils/`. This GNU as knows neither Allegrex nor the VFPU:
  `tools/vfpu_words.py` turns VFPU instructions and the Allegrex-only ones (`min`,
  `max`, `clz`, `madd`... encoded differently on mips32) into `.word`.
- objdiff-cli **v3.8.3** (report, diff), objdiff GUI.
- m2c (matt-kempster/m2c, pinned commit `c632946b`, installed from git: the PyPI
  package named `m2c` is an unrelated project) for a first C draft.
- Compiler: **not identified**. SN Systems SNC is suspected (`notes/COMPILER.md`);
  nothing is compiled from C until it is settled.
- Optional: Ghidra 11.2.1 with ghidra-allegrex, outside the repository.
  PPSSPP for runtime debugging.

## Build pipeline

1. `tools/prx_reloc.py --absolute`: the original PRX with every reference to program
   header 1 made absolute, so the disassembly gets the right symbols.
2. splat splits that image: ELF header and the tail (`.shstrtab`, section headers,
   relocation tables, `.symtab`) as `bin`, program header 0 as text, rodata and data
   regions, program header 1 as `.sdata` + bss.
3. `as` / `objcopy -I binary`, then `ld` with the splat linker script, `objcopy -O
   binary`: the absolute image.
4. `tools/prx_reloc.py --relative` gives the PRX back; `tools/sha1.py` checks it.

The relocation tables are still copied from the original (`elf_tail.bin`): this holds
while the layout does not move, which a matching build guarantees. Generating them
from the link is a later task.

## Acceptance criteria

- Every build ends with `build/NPUG80330/LEVELSTARTUP_DISC.PRX: OK` (`ninja`),
  locally and in CI.
- A unit is matching only when objdiff reports 100 % for all its functions and data
  and the build still matches. Anything else keeps its `INCLUDE_ASM` functions, with
  the remaining gap written above each unfinished function.
- A split that builds proves the bytes, not the translation unit: a TU boundary is
  proven only once the unit is decompiled and matches (`notes/SPLITS.md`).
- Every name, compiler fact or structure layout rests on evidence (strings with their
  address, import/export tables, library signatures, an objdiff diff, a build
  result). Without evidence it is labelled a hypothesis. Names given in Ghidra or by
  m2c are not evidence by themselves.
- Reused code or data from another project is logged with its commit and license in
  `notes/PROVENANCE.md`.

## Naming conventions

- splat default names stay until proven: `func_<vram>`, `D_<vram>`, `jtbl_<vram>`.
- System imports: the NID's name from `config/nids.txt` (PPSSPP HLE tables). `mcp`
  imports: `mcp_<NID>` until the EBOOT export is identified.
- Module exports: the standard SDK names of their NIDs (`module_start`...).
- Game units: `src/<path from the source string>` when a source path is proven by a
  string the unit uses (`v:/PROJECTS/JAK1/CODE/ENGINE/video.cpp` gives
  `src/ENGINE/video.cpp`), otherwise `src/unit_<start vram>.cpp`.
- Unknown classes and structs: `Unk<Name>` or `Unk<address>`.
- Code, comments, notes and commit messages are in English.

## Repository layout

```
README.md SPEC.md LICENSE
config/nids.txt           NID -> name (generated from PPSSPP)
config/NPUG80330/         build.sha1, splat.levelstartup.yaml, symbol_addrs.txt,
                          symbol_addrs.prx.txt (generated)
orig/NPUG80330/           the ISO and the extracted PRX (git-ignored)
asm/                      splat output (git-ignored)
build/                    build output (git-ignored)
src/  include/            sources and headers
tools/                    configure.py and scripts
progress/NPUG80330/       progress badges and history (README images)
notes/                    reference documentation
.github/workflows/        CI: rebuild and check the PRX in a private image
```

## Build

```
pip install -r tools/requirements.txt
python tools/extract.py      # orig/NPUG80330/<iso> -> LEVELSTARTUP_DISC.PRX, SHA-1 checks
python tools/configure.py    # absolute image, splat, build.ninja
ninja                        # assemble, link, PRX, SHA-1 check
```
