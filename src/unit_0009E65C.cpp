// Unit 0x0009E65C-0x0009E6EC (vram), rodata 0x00110090-0x001100B0, data
// 0x0012DF70-0x0012DF78: callbacks for the vehicle customization screen and a
// static initialization. Bounds: the file ends with its static initialization
// (0x9E6CC, listed in .cplinit), the previous file ends with 0x9E5F4
// (notes/SPLITS.md). Same data and static initialization as unit_0009B834
// (hypothesis: a shared header).

extern "C" {

extern void func_0007F450(int, int);
extern void func_00015FC0(int, int);
extern void func_00066138(int, int, const char*);

void func_0009E65C() {}

void func_0009E664() {}

void func_0009E66C(int flags) {
    if (flags & 0x2000) {
        func_0007F450(0, 0);
        func_00015FC0(4, 0);
    }
}

void func_0009E6A4() { func_00066138(100, 100, "screenVehicleCustomization"); }

float D_0012DF70 = 0.62831855f;

}

// Written only by the static initialization (0x9E6CC): no other code reads it.
static float D_0012DF74 = D_0012DF70 * 0.5f;
