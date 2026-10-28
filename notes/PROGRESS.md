# Progress log

| Date | Commit | Matched code | Matched functions | Units (matching / total) | Milestone |
|---|---|---|---|---|---|
| 2026-10-28 | `a27a0d1` | 44 / 1095140 bytes (0.004 %) | 3 / 4048 | 1 / 1 (plus 2 assembly pieces) | First unit compiled with SNC: `unit_000960A4` |
| 2026-10-28 | `97230e0` | 748 / 1095140 bytes (0.07 %) | 7 / 4048 | 1 / 1 (in 2 files, plus 3 assembly pieces) | `unit_000960A4` extended to 0x96528 (7 of its 8 functions) |
| 2026-10-28 | `09c3082` | 812 / 1095140 bytes (0.07 %) | 12 / 4048 | 2 / 2 (plus 4 assembly pieces) | First unit with its own `.data` and static initialization, bounds from `.cplinit`: `unit_0009B834` |
| 2026-10-28 | `0633ed4` | 1040 / 1095140 bytes (0.09 %) | 22 / 4048 | 4 / 4 (plus 6 assembly pieces) | `unit_0008EBB4` and `unit_0009E65C` (first unit with its own `.rodata`), same `.cplinit` method |
