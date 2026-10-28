#!/usr/bin/env python3
"""Generate build.ninja for the Jak and Daxter: The Lost Frontier decompilation.

Pipeline for each module (SPEC.md, "Build"):

  orig PRX --prx_reloc --absolute--> absolute image --splat--> asm/, linker script
  asm/*.s --vfpu_words--> as --> .o ; src/*.cpp --SNC (compile.py)--> .o ;
  bin/*.bin --objcopy--> .o
  ld (splat linker script) --> .elf --objcopy -O binary--> absolute image
  --prx_reloc --relative--> PRX, checked against config/<version>/build.sha1

objdiff: each C/C++ unit is compared with a target object assembled from the
splat assembly of its functions; the remaining assembly files are target-only
units, so the report covers the whole module.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import ninja_syntax
from get_platform import get_platform

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

VERSIONS = [
    "NPUG80330",  # US, DISC_VERSION 1.00
]

# Modules built per version: name -> (PRX file name, splat config)
MODULES = {
    "levelstartup": ("LEVELSTARTUP_DISC.PRX", "splat.levelstartup.yaml"),
}

BINUTILS_TAG = "v0.10"  # decompals/binutils-mips-ps2-decompals
BINUTILS_PREFIX = "mips-ps2-decompals-"
OBJDIFF_VERSION = "v3.8.3"
WIBO_VERSION = "1.2.0"  # runs the Windows compiler on Linux and macOS
COMPILER = "pspsnc_1.2.7503.0"  # notes/COMPILER.md

# Matched code: SNC at -O2 with debug information (notes/COMPILER.md)
CC_FLAGS = "-O2 -g -Iinclude -Isrc"

AS_FLAGS = "-EL -march=mips32r2 -mabi=32 -G0 -no-pad-sections -Iinclude"
LD_FLAGS = "-EL --no-check-sections"


parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-v", "--version", choices=VERSIONS, default=VERSIONS[0])
parser.add_argument("--binutils", type=Path, help="Directory of pre-installed binutils")
parser.add_argument("--no-split", action="store_true",
                    help="Do not run splat (use the existing asm/ and linker script)")
args = parser.parse_args()

platform = get_platform()
if platform is None:
    sys.exit(1)

version = args.version
build_dir = Path("build") / version
orig_dir = Path("orig") / version
config_dir = Path("config") / version
binutils_dir = args.binutils or Path("tools") / "binutils"
compiler_dir = Path("tools") / "compilers" / COMPILER
python = sys.executable.replace("\\", "/")


def tool(name: str) -> str:
    return str(binutils_dir / f"{BINUTILS_PREFIX}{name}{platform.exe}")


def posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def split(module: str) -> None:
    """Write the absolute image and run splat for one module."""
    prx_name, splat_config = MODULES[module]
    image = build_dir / prx_name.replace(".PRX", ".abs.prx")
    # splat does not delete files of subsegments that were renamed or split
    shutil.rmtree(ROOT / "asm" / version / module, ignore_errors=True)
    subprocess.run([sys.executable, "tools/prx_reloc.py", str(orig_dir / prx_name),
                    str(image), "--absolute"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-m", "splat", "split", str(config_dir / splat_config)],
                   check=True, cwd=ROOT, stdout=subprocess.DEVNULL)


def linker_inputs(ld_script: Path) -> list[str]:
    """Object files named in a splat linker script, in order."""
    objs = []
    for line in (ROOT / ld_script).read_text().splitlines():
        line = line.strip()
        if line.startswith(posix(build_dir)) and "(" in line:
            obj = line.split("(")[0]
            if obj not in objs:
                objs.append(obj)
    return objs


def function_vram(path: Path) -> int:
    """vram of the first instruction of a splat function file."""
    m = re.search(r"/\* [0-9A-F]+ ([0-9A-F]{8}) ", (ROOT / path).read_text())
    return int(m.group(1), 16) if m else 0


def write_target_asm(module: str, unit: str) -> Path | None:
    """Assembly of the original functions of one C/C++ unit, in address order."""
    asm_root = Path("asm") / version / module
    funcs = [f for d in ("matchings", "nonmatchings") for f in (ROOT / asm_root / d / unit).glob("*.s")]
    if not funcs:
        return None
    funcs = sorted((f.relative_to(ROOT) for f in funcs), key=function_vram)
    out = build_dir / "target" / f"{unit}.s"
    (ROOT / out).parent.mkdir(parents=True, exist_ok=True)
    lines = ['.include "macro.inc"', ".set noat", ".set noreorder", '.section .text, "ax"']
    lines += [f'.include "{posix(f)}"' for f in funcs]
    (ROOT / out).write_text("\n".join(lines) + "\n", newline="\n")
    return out


def write_objdiff(units: list[dict]) -> None:
    config = {
        "min_version": "2.3.2",
        "custom_make": "ninja",
        "build_base": True,
        "build_target": False,
        "watch_patterns": ["*.c", "*.cpp", "*.h", "*.hpp", "*.py", "*.yaml", "*.txt"],
        "units": units,
    }
    (ROOT / "objdiff.json").write_text(json.dumps(config, indent=2) + "\n", newline="\n")


def main() -> None:
    n = ninja_syntax.Writer(open(ROOT / "build.ninja", "w", newline="\n"), width=120)
    n.comment("Generated by tools/configure.py, do not edit")
    n.variable("ninja_required_version", "1.10")
    n.variable("python", python)
    n.variable("as_flags", AS_FLAGS)
    n.variable("ld_flags", LD_FLAGS)
    n.variable("cc_flags", CC_FLAGS)
    n.newline()

    binutils_stamp = binutils_dir / f"{BINUTILS_PREFIX}as{platform.exe}"
    n.rule("download_binutils",
           f"$python tools/download_tool.py binutils {BINUTILS_TAG} --path {posix(binutils_dir)}",
           description="DOWNLOAD binutils $tag")
    n.build(posix(binutils_stamp), "download_binutils")
    n.rule("download_objdiff",
           f"$python tools/download_tool.py objdiff {OBJDIFF_VERSION} --path $out",
           description="DOWNLOAD objdiff-cli")
    n.build(f"objdiff-cli{platform.exe}", "download_objdiff")
    snc = compiler_dir / "pspsnc.exe"
    n.rule("download_compiler", f"$python tools/download_tool.py compiler {COMPILER} --path {posix(compiler_dir)}",
           description=f"DOWNLOAD {COMPILER}")
    n.build(posix(snc), "download_compiler")
    cc_deps = [posix(snc)]
    if platform.system == "windows":
        cc_command = str(snc)
    else:
        n.rule("download_wibo", f"$python tools/download_tool.py wibo {WIBO_VERSION} --path $out",
               description="DOWNLOAD wibo")
        n.build("tools/wibo", "download_wibo")
        cc_deps.append("tools/wibo")
        cc_command = f"tools/wibo {posix(snc)}"
    n.newline()

    n.rule("as", f"$python tools/assemble.py {posix(tool('as'))} $in $out $as_flags",
           description="AS $in")
    n.rule("cc", f"$python tools/compile.py {posix(tool('objcopy'))} $out {posix(cc_command)} -c $cc_flags -o $out $in",
           description="CC $in")
    n.rule("bin", f"{tool('objcopy')} -I binary -O elf32-littlemips -B mips $in $out",
           description="BIN $in")
    n.rule("ld", f"{tool('ld')} $ld_flags -T $script $undefined -Map $map -o $out",
           description="LD $out")
    n.rule("objcopy", f"{tool('objcopy')} -O binary $in $out", description="OBJCOPY $out")
    n.rule("relative", "$python tools/prx_reloc.py $in $out --relative", description="PRX $out")
    n.rule("check", "$python tools/sha1.py $in", description="CHECK $in")
    n.rule("configure", f"$python tools/configure.py --version {version}",
           description="CONFIGURE", generator=True)
    n.newline()

    objdiff = r".\objdiff-cli.exe" if platform.system == "windows" else "./objdiff-cli"
    n.rule("report", f"{objdiff} report generate -o $out",
           description="REPORT $out")
    n.newline()

    checks = []
    units = []
    unit_objs = []
    for module, (prx_name, splat_config) in MODULES.items():
        ld_script = build_dir / f"{module}.ld"
        if not args.no_split or not (ROOT / ld_script).exists():
            split(module)
        objs = linker_inputs(ld_script)
        for obj in objs:
            # build/<v>/asm/.../x.s.o <- asm/.../x.s ; build/<v>/src/.../x.cpp.o <- src/.../x.cpp ;
            # build/<v>/bin/x.bin.o <- build/<v>/bin/x.bin
            src = obj[:-2]
            if src.endswith(".s"):
                n.build(obj, "as", src[len(posix(build_dir)) + 1:], implicit=[posix(binutils_stamp)])
                if Path(src).name.startswith("text"):
                    # code not split into units yet
                    units.append({"name": f"asm/{module}/{Path(src).stem}", "target_path": obj,
                                  "metadata": {"complete": False, "auto_generated": True}})
                    unit_objs.append(obj)
            elif src.endswith((".c", ".cpp")):
                source = src[len(posix(build_dir)) + 1:]
                n.build(obj, "cc", source, implicit=cc_deps + [posix(binutils_stamp)])
                unit = Path(source).with_suffix("").relative_to("src").as_posix()
                target_asm = write_target_asm(module, unit)
                # A cpp unit holds matched functions only, so it is always linked from source
                unit_entry = {"name": unit, "base_path": obj,
                              "metadata": {"complete": True, "source_path": source}}
                if target_asm:
                    target_obj = posix(build_dir / "target" / f"{unit}.o")
                    n.build(target_obj, "as", posix(target_asm), implicit=[posix(binutils_stamp)])
                    unit_entry["target_path"] = target_obj
                    unit_objs.append(target_obj)
                units.append(unit_entry)
                unit_objs.append(obj)
            else:
                n.build(obj, "bin", src, implicit=[posix(binutils_stamp)])
        elf = build_dir / f"{module}.elf"
        undefined = [build_dir / "undefined_syms_auto.txt", build_dir / "undefined_funcs_auto.txt"]
        n.build(posix(elf), "ld", objs, implicit=[posix(ld_script)] + [posix(u) for u in undefined],
                variables={"script": posix(ld_script), "map": posix(elf.with_suffix(".map")),
                           "undefined": " ".join(f"-T {posix(u)}" for u in undefined)})
        image = build_dir / f"{module}.bin"
        n.build(posix(image), "objcopy", posix(elf))
        prx = build_dir / prx_name
        n.build(posix(prx), "relative", posix(image))
        check = f"check_{module}"
        n.build(check, "check", posix(config_dir / "build.sha1"), implicit=[posix(prx)])
        checks.append(check)
        n.newline()

    write_objdiff(units)
    report = posix(build_dir / "report.json")
    n.build(report, "report", "objdiff.json", implicit=[f"objdiff-cli{platform.exe}"] + unit_objs)
    n.build("report", "phony", report)
    n.newline()

    # splat reads the symbol and relocation files too: a change must split again
    split_inputs = [posix(config_dir / c) for _, c in MODULES.values()] + [
        posix(config_dir / f) for f in ("symbol_addrs.txt", "symbol_addrs.prx.txt", "reloc_addrs.prx.txt")]
    n.build("build.ninja", "configure", implicit=["tools/configure.py"] + split_inputs)
    n.build("all", "phony", checks)
    n.default("all")
    print("build.ninja written")


main()
