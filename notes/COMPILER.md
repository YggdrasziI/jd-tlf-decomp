# Compiler evidence

Status: **SN Systems SNC; working flags `-O2 -g` (or `-O3 -g`)**. With
`pspsnc_1.2.7503.0 -O2 -g`, 15 of 16 hand-written probe functions are
byte-identical (below), including loops, float code and a constructor. Whether
1.2.7503.0 is the game's exact version is not proven: the remaining mismatch may be
a source difference. A compiler is proven only by byte-identical probes; more probes
(switch, virtual calls, VFPU-free math, larger functions) follow as units are written.

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
| 2026-10-28 | `tools/probes/snc_branch.cpp` (8 functions: loops, early returns, floats) | `pspsnc_1.2.7503.0 -O2` | 1/8: SNC merges and duplicates returns, uses branch-likely |
| 2026-10-28 | same | `-O2` + one `-X<var>=0..5` at a time (alias, callmod, constp, copyp, fcm, flow, inllev, sinllev, mopt, reg, sched, unroll, xopt, zone) | no improvement over `-O2` |
| 2026-10-28 | both probes | **`-O2 -g`** | **15/16** after source fixes (`snc_leaf` 8/8, `snc_branch` 7/8); `-O3 -g` same, `-O1 -g` 0/16 |
| 2026-10-28 | both probes | `-O2 -g` + one `-X<var>` at a time | no improvement over `-O2 -g` |

SNC 1.2.7503.0 reproduces the idioms of the original: `or $rd, $rs, $zero` for moves,
`ori` for small constants, a 16-byte frame with `$ra` at `0($sp)`, `$a0` as the
`%hi` scratch register for loads, constructors returning `this` in `$v0`.

`-g` (debug information) changes code generation: without it SNC duplicates
returns, threads jumps and uses branch-likely; with it, each function keeps a single
epilogue and unthreaded `b` chains (`b .L1; nop` to a `b .L2`), as in the original
(only 71 of its 4048 functions have more than one `jr $ra`).

Source-level findings so far (for `notes/MATCHING.md` once units are written):
- a struct copy `*out = in` emits word moves; field-by-field float copies give the
  original's `lwc1`/`swc1` pairs;
- an argument passed through to a call keeps `$a0` live, which moves temporaries to
  `$a1`; a register-only mismatch can mean a missing parameter;
- `if (b == 0.0f) return 0.0f;` and `return b;` differ (constant reloaded vs
  register reused).

The `-O<n>` groups expand to control variables (strings in `pspsnc.exe`):
`alias callmod constp copyp fcm flow inllev sinllev mopt reg sched unroll xopt zone`.

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
   readable `type_info` names and 15/16 identical probes at `-O2 -g`. decomp.me has one
   build, `pspsnc_1.2.7503.0`; the game's exact version is unknown.
2. **Metrowerks mwccpsp** (sotn-decomp uses 2.19 through `bin/mw`/wibo): EDG-like
   runtime too, but CodeWarrior output usually has different section names.
3. **psp-gcc** (SDK GCC 3.x/4.x): unlikely given the runtime strings.

## Next probes

- Look for known SNC runtime routines (`__sn*`, `_sn_*`), libsn, and the EH table
  format referenced by `.cplinit`/`.data`.
- `func_0002D818`: the original loads `self->key` before `i = 0`; not reproduced yet.
- More probes (switch, virtual calls, larger functions) while writing units.
- mwccpsp through wibo, to rule it out with the same probe.
- Record each test here with its date, its input and its result.
