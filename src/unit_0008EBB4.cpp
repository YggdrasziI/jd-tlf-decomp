// Unit 0x0008EBB4-0x0008EC08 (vram), data 0x0012B160-0x0012B168: four callbacks
// (their addresses are passed together by func_0007FF08) and a static
// initialization. Bounds: the file ends with its static initialization (0x8EBE8,
// listed in .cplinit), the previous file ends with 0x8EA44 (notes/SPLITS.md).
// Same data and static initialization as unit_0009B834 (hypothesis: a shared
// header).

extern "C" {

extern void func_0007E918();

void func_0008EBB4() {}

void func_0008EBBC() { func_0007E918(); }

void func_0008EBD8() {}

void func_0008EBE0() {}

float D_0012B160 = 0.62831855f;

}

// Written only by the static initialization (0x8EBE8): no other code reads it.
static float D_0012B164 = D_0012B160 * 0.5f;
