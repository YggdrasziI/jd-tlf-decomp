# References

## Tools

- [ethteck/splat](https://github.com/ethteck/splat) (`splat64[mips]` 0.50.1, MIT):
  `platform: psp` disassembles Allegrex (rabbitizer `R4000ALLEGREX`); no PRX-specific
  segment type. Local clone: `E:\Projets\Github\Decomp\Tools\PSP\splat` (7548b97),
  docs in `docs/Configuration.md` and `docs/Segments.md`.
- [Decompollaborate/spimdisasm](https://github.com/Decompollaborate/spimdisasm) and
  rabbitizer: disassembler used by splat.
- [decompals/binutils-mips-ps2-decompals](https://github.com/decompals/binutils-mips-ps2-decompals)
  v0.10: Windows/Linux/macOS builds of `as`/`ld`/`objcopy`. They have no
  `-march=allegrex` and no VFPU: the build assembles as `-march=mips32r2 -mabi=32`
  and `tools/vfpu_words.py` emits VFPU and Allegrex-only instructions as `.word`.
  Alternative: [sozud/binutils-allegrex](https://github.com/sozud/binutils-allegrex)
  (used by sotn-decomp, Linux build in its releases).
- [encounter/objdiff](https://github.com/encounter/objdiff): diff and report.
- [matt-kempster/m2c](https://github.com/matt-kempster/m2c) 0.4.7: MIPS to C draft.
- [simonlindholm/asm-differ](https://github.com/simonlindholm/asm-differ),
  [simonlindholm/decomp-permuter](https://github.com/simonlindholm/decomp-permuter):
  optional, once a compiler is known.
- [decompme/compilers](https://github.com/decompme/compilers) and
  [decomp.me](https://decomp.me): PSP compilers (psp-gcc, mwccpsp); not used for
  sharing, the project is private.
- [pspdev/pspdev](https://github.com/pspdev/pspdev): homebrew toolchain (modern
  psp-gcc), for tests and tooling, not for matching.
- [John-K/pspdecrypt](https://github.com/John-K/pspdecrypt) or PPSSPP
  `Core/ELF/PrxDecrypter.cpp`: decrypt `EBOOT.BIN` (step 7).
- Ghidra 11.2.1 (`E:\Projets\Github\Decomp\Tools\Ghidra`) with
  [kotcrab/ghidra-allegrex](https://github.com/kotcrab/ghidra-allegrex) (PRX loader,
  Allegrex + VFPU, NID names), outside the repository.
- PPSSPP (`E:\Projets\Github\Emulateur\PSP\ppsspp`, 8d96fdb6cd, not built locally):
  debugger (breakpoints, memory, disassembly; `.ppmap`/`.sym` symbol maps loaded from
  next to the game, `Core/Debugger/SymbolMap.cpp`), WebSocket debugger API, PRX loader
  (`Core/ELF/ElfReader.cpp`), HLE NID tables (`Core/HLE/*.cpp`, source of
  `config/nids.txt`).
- [TeamGDB/PortableKit](https://github.com/TeamGDB/PortableKit): suggested by the
  owner, not evaluated yet.

## Reference projects (local clones)

Search the local clones (Grep/Glob) before GitHub. A clone may be behind GitHub: ask
the owner before `git pull`. When reusing code, record the clone's commit and the
license in `notes/PROVENANCE.md`.

| Folder | Project | License | Notes |
|---|---|---|---|
| `E:\Projets\Github\Decomp\PSP\sotn-decomp` | [Xeeynamo/sotn-decomp](https://github.com/Xeeynamo/sotn-decomp) (6c7ac7e21) | AGPL-3.0 (check before reuse) | PSP version `pspeu` built with mwccpsp 2.19 (`tools/builds/gen.py`), splat configs `config/splat.pspeu.*.yaml`, VFPU as `.word` (`tools/pspas`), decomp.me PSP preset 132 |

Sibling projects of the owner (methodology, scripts): `E:\Projets\Dev\mlab-decomp`,
`E:\Projets\Dev\spyro-dotd-decomp`, `E:\Projets\Dev\ts2-castaway`.

## Hardware documentation

- CPU Allegrex: MIPS32 R2 subset plus Sony instructions (`min`, `max`, `bitrev`,
  `wsbh`, `ext`, `ins`, `clz`) and the VFPU (128 single-precision registers as 4x4
  matrices).
- To collect: a PSP hardware and SDK reference (memory map, GE command list,
  syscalls). Context only, never evidence for a name or a structure.

## Known pitfalls (from the owner's PSP tool list)

- Disassemblers and m2c handle VFPU poorly: keep VFPU functions in assembly.
- Modules loaded on demand need their own splat config each.
- Several releases of the same game differ: one reference version with its SHA-1
  (`NPUG80330`).
- splat's PSP support is less mature than N64/PSX: read its docs and existing
  projects before relying on an option.

## Reuse permissions

- CC0 and Unlicense projects: allowed, logged in `notes/PROVENANCE.md`.
- No license, GPL or AGPL (sotn-decomp, PPSSPP): ask the owner before reusing code;
  facts (NID names) and ideas are fine and logged.
