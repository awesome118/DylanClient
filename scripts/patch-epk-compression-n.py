#!/usr/bin/env python3
"""Teach the compiled browser EPK reader about the shell's pre-inflated payload marker."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch-epk-compression-n.py /path/to/EPKDecompiler.java")

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

needle = "case '0':\r\n\t\t\t\tzis = is;\r\n\t\t\t\tbreak;"
replacement = (
    "case '0':\r\n"
    "\t\t\tcase 'N': // The HTML shell already inflated this EPK payload.\r\n"
    "\t\t\t\tzis = is;\r\n"
    "\t\t\t\tbreak;"
)

if replacement in source:
    print(f"Already patched: {path}")
    raise SystemExit(0)

if needle not in source:
    raise SystemExit(f"Could not locate the expected EPK compression switch in {path}")

path.write_text(source.replace(needle, replacement, 1), encoding="utf-8")
print(f"Patched {path}: EPK compression marker N is read without a second decompression")
