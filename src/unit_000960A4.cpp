// Unit 0x000960A4-0x00096528 (vram), first part (0x960A4-0x9630C): a selection
// { type, id, handle } in D_0012C01C and the functions that update it. The second
// part is unit_000960A4_1.cpp (func_000964A4); func_0009630C between them is still
// assembly.
// Bounds are a hypothesis: these functions share D_0012C280, D_0012C01C and
// D_0012C278; func_00096528 (an empty function) and the code after it are not
// checked yet.

extern "C" {

struct Selection {
    int type;
    int id;
    int handle;
};

struct Entry {
    int type;
    int unk4;
    int id;
};

struct EntryList {
    Entry** items;
    unsigned int count;
    char unk8[0x10];
    unsigned int current;

    Entry* Current() {
        unsigned int i = current;
        if (i >= count) return 0;
        return items[i];
    }
};

extern Selection D_0012C01C;
extern unsigned char D_0012C278;
extern int D_0012C280;
extern int D_0012BFE8;
extern EntryList D_001D94C0;

extern char* func_000BBFE8(int);
extern int func_000BC22C(int);
extern void func_000BD344(int, int, unsigned int);
extern void func_000BE330(int, int);
extern unsigned char func_00097150();

void func_000964A4(int type, int id, Selection* out);

int func_000960A4() { return D_0012C280; }

bool func_000960B0() { return D_0012C280 == -1; }

void func_000960C4(int value) { D_0012BFE8 = value; }

int func_000960D0(int start) {
    if (start == -1) start = 0;
    if ((unsigned int)start >= 5) start = 0;
    for (unsigned int i = start; i < 6; i++) {
        if (func_000BC22C(i) == 3) return i;
    }
    return -1;
}

int func_00096160(int start) {
    if (start == -1) start = 5;
    if ((unsigned int)start >= 6) start = 5;
    for (int i = start; i >= 0; i--) {
        if (func_000BC22C(i) == 3) return i;
    }
    return -1;
}

void func_000961E8() {
    if (D_0012C01C.type == 1) {
        char* p = func_000BBFE8(D_0012C280);
        unsigned int n = ((unsigned int*)(p + 0x3A0))[D_0012C01C.id];
        for (unsigned int i = 0; i < n; i++) {
            func_000BD344(D_0012C280, D_0012C01C.id, i);
        }
    } else {
        func_000BE330(D_0012C280, D_0012C01C.id);
    }
    Entry* e = D_001D94C0.Current();
    if (e && e->type) {
        func_000964A4(e->type, e->id, &D_0012C01C);
    }
    D_0012C278 = func_00097150();
}

// func_0009630C (0x9630C-0x964A4) stays assembly (asm piece text_0009630C):
// the best source gives the same code except one register copy. The original
// copies `owner` to $s2 before testing it a second time (`or $s2, $a0, $zero;
// beqz $s2`), and swaps the registers of the loop counter and the list pointer.
// Best attempt so far:
//   if (!owner) return;
//   bool invalid = false;
//   if (D_0012C280 == -1) return;
//   switch (D_0012C01C.type) {
//   default: break;
//   case 2: invalid = D_0012C01C.handle == -1; break;
//   case 1: invalid = D_0012C01C.handle == -1; break;
//   }
//   if (invalid && owner) {
//       int obj = owner->unkD8;
//       if (owner->unkDC == 1) {
//           int list[49];
//           Resource* r = func_000BCE2C(obj);
//           unsigned int count = func_000BCC08(r->inner->unk4, list);
//           unsigned int n = ((unsigned int*)(func_000BBFE8(D_0012C280) + 0x3A0))[D_0012C01C.id];
//           int* it = list;
//           for (unsigned int i = 0; i < count && i < 5 && i < n; i++, it++)
//               func_000BD2A8(*it, D_0012C280, D_0012C01C.id, i, 0);
//       } else {
//           func_000BE1E4(obj, D_0012C280, D_0012C01C.id);
//       }
//   }
//   D_0012C278 = func_00097150();

}
