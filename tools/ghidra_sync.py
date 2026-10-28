#!/usr/bin/env python3
"""Sync the Ghidra project with the splat symbol files, without the Ghidra GUI.

Runs Ghidra's analyzeHeadless with tools/ghidra/SyncSymbols.java on the imported PRX:
every symbol of config/<version>/symbol_addrs*.txt is named at its address (link
address + the program's image base), and a function is created for `type:func`
symbols. Names set by hand in Ghidra are kept and listed. Needs Ghidra 12.2 with the
ghidra-allegrex v21.5 extension and a JDK 25 (notes/GHIDRA.md); --ghidra, --jdk and
--project override the default paths.

Usage:
  python tools/ghidra_sync.py --import    # first time: create the project, import
                                          # and analyze the PRX, then sync
  python tools/ghidra_sync.py             # sync
  python tools/ghidra_sync.py --dry-run   # report what would change, change nothing
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_GHIDRA = r"E:\Projets\Github\Decomp\Tools\Ghidra\ghidra_12.2_PUBLIC"
DEFAULT_JDK = r"E:\Projets\Github\Decomp\Tools\Ghidra\jdk-25.0.5+8"
DEFAULT_PROJECT = r"E:\Projets\Dev\jd-tlf-ghidra"
PROJECT_NAME = "jd_tlf"
PRX = "LEVELSTARTUP_DISC.PRX"
SYMBOL_FILES = ("symbol_addrs.prx.txt", "symbol_addrs.txt")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", default="NPUG80330", help="game version (default: %(default)s)")
    parser.add_argument("--ghidra", default=DEFAULT_GHIDRA, help="Ghidra install dir")
    parser.add_argument("--jdk", default=DEFAULT_JDK, help="JDK 25 dir (Ghidra 12.2 needs it)")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help="Ghidra project dir")
    parser.add_argument("--import", dest="do_import", action="store_true",
                        help="import and analyze the PRX first")
    parser.add_argument("--dry-run", action="store_true", help="change nothing")
    args = parser.parse_args()

    headless = os.path.join(args.ghidra, "support",
                            "analyzeHeadless.bat" if os.name == "nt" else "analyzeHeadless")
    if not os.path.isfile(headless):
        sys.exit(f"{headless} not found (--ghidra)")
    os.makedirs(args.project, exist_ok=True)

    # analyzeHeadless is a batch file on Windows: cmd.exe splits arguments at the
    # "&" of the project folder, so every input is copied to a temporary folder
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(ROOT, "tools", "ghidra", "SyncSymbols.java"), tmp)
        symbols = []
        for name in SYMBOL_FILES:
            symbols.append(shutil.copy(os.path.join(ROOT, "config", args.version, name), tmp))
        cmd = [headless, args.project, f"{PROJECT_NAME}_{args.version}"]
        if args.do_import:
            # The PSP PRX loader of ghidra-allegrex is picked by its file format
            cmd += ["-import", shutil.copy(os.path.join(ROOT, "orig", args.version, PRX), tmp)]
        else:
            cmd += ["-process", PRX, "-noanalysis"]
        cmd += ["-scriptPath", tmp, "-postScript", "SyncSymbols.java", *symbols]
        if args.dry_run:
            cmd.append("dry")
        env = dict(os.environ, JAVA_HOME=args.jdk)
        out = subprocess.run(cmd, capture_output=True, text=True, env=env)
    lines = [line.strip() for line in (out.stdout + out.stderr).splitlines()]
    for line in lines:
        if "SyncSymbols" in line or line.startswith(("ERROR", "INFO  REPORT", "INFO  IMPORTING")):
            print(line)
    # Ghidra log lines start with their level; symbol names may contain "ERROR".
    errors = [line for line in lines if line.startswith("ERROR")]
    return 0 if out.returncode == 0 and not errors else 1


if __name__ == "__main__":
    sys.exit(main())
