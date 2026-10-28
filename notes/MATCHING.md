# Matching techniques

Techniques that fixed a near-miss in this project, with the function where they were
found. Empty sections are placeholders until the compiler is known (`notes/COMPILER.md`).

## MIPS / Allegrex basics to keep in mind

- Branch delay slots: the instruction after a branch or jump runs before the target;
  the compiler fills the slot, so a source reorder can move an instruction into or out
  of a slot.
- `$gp`-relative access (`.sdata`/`.sbss`, `$gp` = 0x148898): variables small enough
  for the small-data threshold are reached through `$gp`; the threshold is a compiler
  flag (`-G`).
- Floats: single precision FPU (`lwc1`, `mul.s`, `c.lt.s` + `bc1t`); no doubles in
  hardware.
- VFPU: assembled as `.word` (`tools/vfpu_words.py`); in C it needs inline assembly or
  intrinsics, so VFPU functions stay assembly until the compiler's VFPU support is
  known.

## Loads, aliasing and const

## Registers and stack

## Floats

## Inlining and emission order

## Data layout

- A file's own `.data` is a `.data` subsegment of its unit in the data segment
  (`[<rom>, .data, <unit>]`, then a `data_<vram>` piece for the rest); globals keep
  their `D_<addr>` names, in `extern "C"`.
- A global initialized from another global (`float b = a * 0.5f;`) is a dynamic
  initialization: code in `__sti__<file>` and a 0 in `.data`. A non-static one
  goes to COMMON (`.bss`), a `static` one stays in `.data` after the file's
  initialized globals (`unit_0009B834`).
- The static initialization is named by SNC after the path given to it:
  `__sti__src_<unit>_cpp`. Put that name in `symbol_addrs.txt` at its address;
  `tools/compile.py` makes it global for the `.cplinit` table.

## Control flow

## C++ classes, virtual calls and RTTI

## Unsolved patterns
