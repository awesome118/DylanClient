#!/usr/bin/env python3
"""Teach the compiled browser EPK reader about the shell's pre-inflated payload marker."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch-epk-compression-n.py /path/to/EPKDecompiler.java")

path = Path(sys.argv[1])
raw = path.read_bytes()
newline = "\r\n" if b"\r\n" in raw else "\n"
source = raw.decode("utf-8")

needle = "case '0':" + newline + "\t\t\t\tzis = is;" + newline + "\t\t\t\tbreak;"
replacement = (
    "case '0':" + newline
    + "\t\t\tcase 'N': // The HTML shell already inflated this EPK payload." + newline
    + "\t\t\t\tzis = is;" + newline
    + "\t\t\t\tbreak;"
)

if replacement in source:
    print(f"Already patched: {path}")
    raise SystemExit(0)

if needle not in source:
    raise SystemExit(f"Could not locate the expected EPK compression switch in {path}")

path.write_bytes(source.replace(needle, replacement, 1).encode("utf-8"))
print(f"Patched {path}: EPK compression marker N is read without a second decompression")
