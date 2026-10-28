# Compiler evidence

Status: **SN Systems SNC, most likely; version not settled**. SNC 1.2.7503.0 at `-O2`
gives byte-identical code for 6 of 8 probe functions (below). The two others differ
in branch layout and register choice, which may mean another SNC version, other
flags or other source; no conclusion yet. A compiler is proven only by
byte-identical probes.

## Probes

`python tools/compiler_probe.py <src> [--cc <exe>] -- <flags>` compiles a probe and
compares every function named `func_XXXXXXXX` with the original at that vram,
relocated fields masked. Compilers come from the decomp.me releases
(`https://github.com/decompme/compilers/releases/download/compilers/<id>.tar.gz`) and
are unpacked in `tools/compilers/<id>/` (ignored by git).

| Date | Probe | Compiler, flags | Result |
|---|---|---|---|
| 2026-10-28 | `tools/probes/snc_leaf.cpp` (8 small leaf functions) | `pspsnc_1.2.7503.0 -O2` (`-O3` same) | **6/8 identical**: `func_00015F6C`, `func_000225A8`, `func_00027728`, `func_0007F95C` (a constructor returning `this`), `func_000960A4`, `func_00109318` |
| 2026-10-28 | same | `pspsnc_1.2.7503.0 -O0`, `-O1` | 0/8 (unoptimised code) |
| 2026-10-28 | same | `-O2 -Xretpts=0` / `=1` | no change, 6/8 |
| 2026-10-28 | `func_0007E6D8`, 9 source variants (single return, `goto`, `bool`, `?:`) | `pspsnc_1.2.7503.0 -O2` | no match: SNC duplicates `jr $ra`, the original branches to a single epilogue |
| 2026-10-28 | `func_001051AC`, 4 variants (extra parameters, member function, local copy) | `pspsnc_1.2.7503.0 -O2` | no match: the original uses `$a1` for the loaded pointer, SNC `$a0` |
| 2026-10-28 | `snc_leaf.cpp` | `mwccpsp_3.0.1_219` run natively | did not finish (hangs, likely the licence manager); to retry through wibo |

SNC 1.2.7503.0 reproduces the idioms of the original: `or $rd, $rs, $zero` for moves,
`ori` for small constants, a 16-byte frame with `$ra` at `0($sp)`, `$a0` as the
`%hi` scratch register for loads, constructors returning `this` in `$v0`.

Only 71 of the 4048 functions of the original have more than one `jr $ra`; SNC
1.2.7503.0 at `-O2` duplicates returns readily. If that holds on more probes, the
game used another SNC version (or a flag not found yet).

`psp-gcc-1.3.1` from decomp.me is a Linux i386 build and was not run (Windows host,
no WSL).

## Clues (2026-10-27, LEVELSTARTUP_DISC.PRX)

| Clue | Where | Points to |
|---|---|---|
| Sections `.cplinit` (0x2C8 bytes, 88 R_MIPS_32) and `.linkonce.d` | section headers | SN Systems toolchain (ProDG / SNC + SN linker); GCC uses `.init_array`/`.ctors` and `.gnu.linkonce.*` |
| `type_info` names in plain text: `std::bad_alloc`, `std::exception`, `std::bad_exception`, `std::type_info` | `.rodata` 0x114AB0-0x114CC8 | not GCC (libsupc++ stores mangled names such as `St9bad_alloc`); EDG-based runtimes (SNC, Metrowerks) store readable names |
| `terminate() called by the exception handling mechanism` | `.rodata` 0x114AE4 | a C++ runtime other than libsupc++ (to compare with SNC and Metrowerks runtimes) |
| `move` emitted as `or $rd, $rs, $zero`, small constants as `ori $rd, $zero, imm` | `.text` everywhere (`or` 22527 times, `ori` 13467) | GCC for Allegrex emits `addu`/`move` and `addiu`/`li`; to compare with SNC and mwccpsp output |
| Source paths `v:/PROJECTS/JAK1/CODE/...cpp` | `.rodata` | C++ code; the `v:` drive and forward slashes say nothing about the compiler |
| SDK version word `0x05050010` | `module_sdk_version` (0x10E1A0) | PSP SDK 5.5.0 (hypothesis from the encoding used by other modules) |
| ELF flags 0x10A23001 | ELF header | standard PSP value; not discriminating |
| Empty `.symtab`, 0x74-byte `.eh_frame` | section headers | stripped module; exception tables are elsewhere (to find) |

## Candidates

1. **SN Systems SNC** (ProDG for PSP): favoured by `.cplinit`, `.linkonce.d`, the
   readable `type_info` names and the 6/8 identical probes. decomp.me has one
   build, `pspsnc_1.2.7503.0`; the game's exact version is unknown.
2. **Metrowerks mwccpsp** (sotn-decomp uses 2.19 through `bin/mw`/wibo): EDG-like
   runtime too, but CodeWarrior output usually has different section names.
3. **psp-gcc** (SDK GCC 3.x/4.x): unlikely given the runtime strings.

## Next probes

- Look for known SNC runtime routines (`__sn*`, `_sn_*`), libsn, and the EH table
  format referenced by `.cplinit`/`.data`.
- More probes (loops, switch, floats, C++ virtual calls) to tell whether the
  single-return layout is a version difference or a source difference.
- SNC control variables (`pspsnc -X...`; strings in `pspsnc.exe`/`pspcq.exe`) that
  change block layout or register allocation.
- mwccpsp through wibo, to rule it out with the same probe.
- Record each test here with its date, its input and its result.
