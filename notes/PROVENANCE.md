# Provenance of reused code and data

Every file, function or data set taken from another project, with the project, its
commit (`git -C <clone> rev-parse HEAD`), its license (or its absence and the owner's
approval, see `notes/REFERENCES.md`) and the changes made.

## Tools (`tools/psp`, `tools/common`)

The scripts first written or adapted in this repository (PRX reader and relocation
passes, VFPU words, compiler wrapper and probe, candidates, report gate, progress
card, build helpers) now come from two submodules of the owner, both CC0-1.0, which
record their own provenance (their `README.md`):

- `tools/psp`: [psp-decomp-tools](https://github.com/YggdrasziI/psp-decomp-tools);
- `tools/common`: [decomp-tools](https://github.com/YggdrasziI/decomp-tools).

Only `tools/configure.py` and `tools/extract.py` stay here, written for this project.

`LICENSE` (CC0-1.0) is the same as the sibling projects'.

## NID names (`tools/psp/nids.txt`)

The list first generated here now comes with `tools/psp`. Source: PPSSPP
(`Core/HLE/*.cpp`), local clone at commit
`8d96fdb6cd65753b00c713b02fa6d2fb857d21ec`, license GPL-2.0-or-later. Only the facts
NID -> function name are extracted (`tools/psp/prx_symbols.py --ppsspp`), no code.

## Ideas without code

- VFPU instructions assembled as `.word` from splat's comment: idea of sotn-decomp's
  `tools/pspas` (AGPL-3.0); `tools/psp/vfpu_words.py` is written from scratch.
- HI16/LO16 pairing of PRX relocations: behaviour of PPSSPP's
  `ElfReader::LoadRelocations`; `tools/psp/prx_reloc.py` is written from scratch.

## Project documents

`SPEC.md` and `notes/` follow the
structure of the owner's ts2-castaway project, rewritten for the PSP toolchain.
