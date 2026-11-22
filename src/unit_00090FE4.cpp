// Unit 0x00090FE4-0x00091038 (vram), data 0x0012B8D8-0x0012B8E0: four callbacks
// (their addresses are passed together to func_0007E774 with the id 0x28, at
// 0x7FEE0) and a static initialization. Bounds: the file ends with its static
// initialization (0x91018, listed in .cplinit). The start is a hypothesis: the
// same four callbacks, data and initialization as unit_0008EBB4, but the previous
// .cplinit entry ends at 0x90C90, so the file may start earlier.

extern "C" {

extern void func_0007E918();

void func_00090FE4() {}

void func_00090FEC() { func_0007E918(); }

void func_00091008() {}

void func_00091010() {}

float D_0012B8D8 = 0.62831855f;

}

// Written only by the static initialization (0x91018): no other code reads it.
static float D_0012B8DC = D_0012B8D8 * 0.5f;
