# PRX format and build pipeline

What the PSP module format means for this project, checked on
`LEVELSTARTUP_DISC.PRX` (`python tools/prx_info.py`). Loader behaviour follows PPSSPP
(`Core/ELF/ElfReader.cpp`, local clone at `8d96fdb6cd`), which is a reimplementation,
not Sony's loader: anything only PPSSPP says is a hypothesis.

## File layout

| File offset | Content |
|---|---|
| 0x000000 | ELF header (type 0xFFA0 = PRX, machine MIPS, flags 0x10A23001), 2 program headers |
| 0x000074 | program header 0, vram 0x0: `.text`, `.sceStub.text.*`, `.rodata.sceResident`, `.lib.ent*`, `.lib.stub*`, `.rodata.sceModuleInfo`, `.rodata.sceNid`, `.rodata`, `.data`, `.eh_frame`, `.sceStub.text.mcp`, `.ctors`, `.dtors`, `.cplinit`, `.psp_lib_markimport_`, `.psp_lib_mark_`, `.linkonce.d` |
| 0x140918 | program header 1, vram 0x1408A8: `.sdata` (0x18 bytes); `.sbss` and `.bss` have no file data |
| 0x140930 | `.shstrtab`, section headers (0x140CD0), relocation tables (0x141590-0x189278), empty `.symtab`, `.strtab` |

Section file offset = vram + 0x74 in program header 0. The section header order is
not the address order (`.rodata.sceResident`, index 28, sits at 0x10B964 between the
stubs and `.lib.ent.top`).

## Relocations

Tables of type `SHT_PRXRELOC` (0x700000A0), `Elf32_Rel` entries where `r_info` is
not the standard ELF encoding:

- bits 0-7: type (2 = R_MIPS_32, 4 = R_MIPS_26, 5 = R_MIPS_HI16, 6 = R_MIPS_LO16);
- bits 8-15: program header that `r_offset` is relative to;
- bits 16-23: program header whose base the loader adds to the value.

At load time the loader adds the base of the "address" program header. For program
header 0 the stored values are already the final addresses minus 0 (vram 0x0), but
for program header 1 they are relative to **its** base: `lui $a0, 0x0; addiu $a0,
$a0, 0x170` means `.bss` 0x140A18 (0x1408A8 + 0x170), not `.text` 0x170.

HI16 pairing (PPSSPP): a HI16 takes the low half of the next entry of the same table
that is not a HI16; every value is computed from the words read before any patching.

`tools/prx_reloc.py --absolute` adds the base of program header 1 at those sites
(6197 bytes change); `--relative` undoes it. Round trip checked on the original:
identical SHA-1 (2026-10-27).

## Imports and exports

- `.lib.stub` (from `module_info.stub_top` to `stub_end`): one 20-byte entry per
  library: name pointer, version, flags, entry size (5 words), variable count,
  function count, NID table pointer, stub table pointer. Each function stub is 8
  bytes, patched by the loader. 16 libraries: 15 system libraries (124 functions) and
  `mcp` (92 functions, stubs in `.sceStub.text.mcp`).
- `mcp` is the module in `SYSDIR/EBOOT.BIN` (`~PSP` header, module name `mcp`): the
  EBOOT exports functions to the level modules. Its NID names are unknown until the
  EBOOT is decrypted.
- `.lib.ent`: one export library (the module's own) with the standard SDK NIDs:
  `module_start` 0xF197C, `module_stop` 0xF1B04, `module_info` 0x10BC1C,
  `module_sdk_version` 0x10E1A0 (value `0x05050010`), `module_start_thread_parameter`
  0x114A94, `module_stop_thread_parameter` 0x114A84.
- `tools/prx_symbols.py` writes all of these to `config/NPUG80330/symbol_addrs.prx.txt`;
  NID names come from `config/nids.txt` (PPSSPP HLE tables, `--ppsspp` to rebuild).

## Build pipeline

```
orig PRX --prx_reloc --absolute--> build/NPUG80330/LEVELSTARTUP_DISC.abs.prx
         --splat--> asm/NPUG80330/levelstartup/*.s, build/NPUG80330/bin/elf_{header,tail}.bin,
                    build/NPUG80330/levelstartup.ld
*.s --tools/assemble.py (vfpu_words + as)--> .o ; *.bin --objcopy -I binary--> .o
src/*.cpp --tools/compile.py (SNC -O2 -g, empty sections removed)--> .o
ld -T levelstartup.ld --> levelstartup.elf --objcopy -O binary--> levelstartup.bin
   --prx_reloc --relative--> LEVELSTARTUP_DISC.PRX --sha1--> OK
```

The PRX relocation tables are the reference for what is an address:
`tools/reloc_overrides.py` writes a `MIPS_NONE` override (`config/NPUG80330/
reloc_addrs.prx.txt`) for every `%hi`/`%lo` or `.word` symbol of the splat output
that has no relocation. Without them, constants such as `lui $a0, 0x7; addiu $a0,
0x6B10` became references to code labels (`.L00076B10`) that break the link once
`.text` is in several files; most entries are zero data words (null pointers).
`%gp_rel` operands are relative to `$gp` and never relocated, so they are kept.

splat groups the entries of one segment by section type in `section_order`
(`.text`, `.rodata`, `.data`, `.bss`), so the yaml keeps each type in one contiguous
region: text (`.text` + system stubs), rodata (`.rodata.sceResident` to `.rodata`),
data (`.data` to `.linkonce.d`, `mcp` stubs included as data). `ld_align_*` options
are off and segments use `align: 4` so no padding is inserted.
