// Unit 0x000960A4-0x000960D0 (vram): three accessors of globals.
// Bounds are a hypothesis: the functions after 0x960D0 use D_0012C280 too and
// may belong to the same source file.

extern "C" {

extern int D_0012BFE8;
extern int D_0012C280;

int func_000960A4() { return D_0012C280; }

bool func_000960B0() { return D_0012C280 == -1; }

void func_000960C4(int value) { D_0012BFE8 = value; }

}
