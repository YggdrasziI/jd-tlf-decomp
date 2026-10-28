// Unit 0x0009B834-0x0009B874 (vram), data 0x0012CA90-0x0012CA98: four empty callbacks
// (their addresses are passed together by func_0007FAF8) and a static initialization.
// Bounds: the file ends with its static initialization (0x9B854, listed in
// .cplinit), the previous file ends with 0x9B7F4 (notes/SPLITS.md).

extern "C" {

void func_0009B834() {}

void func_0009B83C() {}

void func_0009B844() {}

void func_0009B84C() {}

float D_0012CA90 = 0.62831855f;

}

// Written only by the static initialization (0x9B854): no other code reads it.
static float D_0012CA94 = D_0012CA90 * 0.5f;
