# Provenance of reused code and data

Every file, function or data set taken from another project, with the project, its
commit (`git -C <clone> rev-parse HEAD`), its license (or its absence and the owner's
approval, see `notes/REFERENCES.md`) and the changes made.

## Build helpers (`tools/`)

Source: [Yotona/twewy](https://github.com/Yotona/twewy), license **CC0-1.0**, through
the owner's ts2-castaway project.

| Our file | Changes |
|---|---|
| `tools/ninja_syntax.py`, `tools/get_platform.py` | none |
| `tools/download_tool.py` | `dsd`/`mwccarm` removed; `binutils` (decompals) and `compiler` (decomp.me archives) added, `.tar.gz` support, HTTP status check |

## Report and progress scripts (`tools/`)

Source: the owner's ts2-castaway project (its own code), 2026-10-28.

| Our file | Changes |
|---|---|
| `tools/report_diff.py` | version `NPUG80330`; assembly pieces (`asm/...`) instead of dsd gaps |
| `tools/progress_badges.py` | title and version; function addresses from `func_<addr>` names and the splat symbol files instead of dsd `symbols.txt`; no regions yet |
| `tools/unit_candidates.py` | rewritten for the splat assembly (`jal` calls, VFPU functions skipped); same output and options |
| `tools/asm_compare.py` | usage examples for this project; assembly pieces have no right side |

`LICENSE` (CC0-1.0) is the same as the sibling projects'.

## NID names (`config/nids.txt`)

Source: PPSSPP (`Core/HLE/*.cpp`), local clone at commit
`8d96fdb6cd65753b00c713b02fa6d2fb857d21ec`, license GPL-2.0-or-later. Only the facts
NID -> function name are extracted (`tools/prx_symbols.py --ppsspp`), no code.

## Ideas without code

- VFPU instructions assembled as `.word` from splat's comment: idea of sotn-decomp's
  `tools/pspas` (AGPL-3.0); `tools/vfpu_words.py` is written from scratch.
- HI16/LO16 pairing of PRX relocations: behaviour of PPSSPP's
  `ElfReader::LoadRelocations`; `tools/prx_reloc.py` is written from scratch.

## Project documents

`SPEC.md` and `notes/` follow the
structure of the owner's ts2-castaway project, rewritten for the PSP toolchain.
