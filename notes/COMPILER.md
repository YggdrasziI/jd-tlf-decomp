# Compiler evidence

Status: **not identified**. Every item below is a clue with its source; none proves a
compiler. A compiler is proven only by byte-identical probes.

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

1. **SN Systems SNC** (ProDG for PSP): favoured by `.cplinit`, `.linkonce.d` and the
   readable `type_info` names. Not on decomp.me as far as known (to check); a
   commercial SDK compiler, so availability is the main risk.
2. **Metrowerks mwccpsp** (sotn-decomp uses 2.19 through `bin/mw`/wibo): EDG-like
   runtime too, but CodeWarrior output usually has different section names.
3. **psp-gcc** (SDK GCC 3.x/4.x): unlikely given the runtime strings.

## Next probes

- Look for known SNC runtime routines (`__sn*`, `_sn_*`), libsn, and the EH table
  format referenced by `.cplinit`/`.data`.
- Compile small leaf functions (setters, `memset`-like loops) with every available
  PSP compiler on decomp.me (preset list) and compare.
- Record each test here with its date, its input and its result.
