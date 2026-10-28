// Unit 0x000960A4-0x00096528 (vram), second part (0x964A4-0x96528): see
// unit_000960A4.cpp; func_0009630C between the two parts is still assembly.

extern "C" {

struct Selection {
    int type;
    int id;
    int handle;
};

extern int D_0012C280;

extern int func_000BC124(int, int);
extern int func_000BC1C4(int, int);

void func_000964A4(int type, int id, Selection* out) {
    out->type = type;
    out->id = id;
    switch (type) {
    case 1:
        out->handle = func_000BC124(D_0012C280, id);
        break;
    case 2:
        out->handle = func_000BC1C4(D_0012C280, id);
        break;
    }
}

}
