#!/usr/bin/env python3
"""Replace the embedded client Wasm, preserve the custom HTML shell, then split it."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

CHUNK_BYTES = 18_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: replace-client-wasm-and-split.py ORIGINAL_HTML CLASSES_WASM_BR REPO_ROOT")

    original_path = Path(sys.argv[1])
    compressed_path = Path(sys.argv[2])
    repo = Path(sys.argv[3])
    original = original_path.read_bytes()
    compressed = compressed_path.read_bytes()

    pattern = re.compile(
        rb'(<script type="application/octet-stream" id="eag-inline-wasm-br" data-size=")\d+(">).*?(</script>)',
        re.DOTALL,
    )
    match = pattern.search(original)
    if not match:
        raise SystemExit("Original client did not contain the expected eag-inline-wasm-br payload.")

    encoded = base64.b64encode(compressed).decode("ascii")
    encoded_lines = "\n".join(encoded[i:i + 256 * 1024] for i in range(0, len(encoded), 256 * 1024))
    replacement = (
        match.group(1)
        + str(len(compressed)).encode("ascii")
        + match.group(2)
        + b"\n"
        + encoded_lines.encode("ascii")
        + b"\n"
        + match.group(3)
    )
    rebuilt = original[:match.start()] + replacement + original[match.end():]

    part_files: list[dict[str, object]] = []
    for old in repo.glob("client.part*.bin"):
        old.unlink()

    for offset in range(0, len(rebuilt), CHUNK_BYTES):
        number = len(part_files) + 1
        name = f"client.part{number:02d}.bin"
        chunk = rebuilt[offset:offset + CHUNK_BYTES]
        (repo / name).write_bytes(chunk)
        part_files.append({"file": name, "bytes": len(chunk), "sha256": sha256(chunk)})

    loader_path = repo / "index.html"
    loader = loader_path.read_text(encoding="utf-8")
    parts_literal = "  const parts = [\n" + ",\n".join(
        f'      "{item["file"]}"' for item in part_files
    ) + "\n  ];"
    loader, parts_count = re.subn(
        r"  const parts = \[.*?\];",
        parts_literal,
        loader,
        count=1,
        flags=re.DOTALL,
    )
    loader, bytes_count = re.subn(
        r"  const expectedBytes = \d+;",
        f"  const expectedBytes = {len(rebuilt)};",
        loader,
        count=1,
    )
    if parts_count != 1 or bytes_count != 1:
        raise SystemExit("Could not update the loader's part list and expected byte count.")
    loader_path.write_text(loader, encoding="utf-8")

    manifest = {
        "client": "eaglercraft-26.2-r1b-nomusic.html",
        "clientBytes": len(rebuilt),
        "clientSha256": sha256(rebuilt),
        "embeddedWasm": {
            "payloadId": "eag-inline-wasm-br",
            "compressedBytes": len(compressed),
            "compressedSha256": sha256(compressed),
            "source": "target_teavm_wasm_gc/build/generated/teavm/wasm-gc-fast-analysis/classes.wasm",
        },
        "patch": {
            "name": "NoMoreResourcePacks",
            "behavior": "Acknowledge required server resource packs without downloading or reloading them.",
            "textures": "Server-provided pack textures are not loaded.",
        },
        "parts": part_files,
    }
    (repo / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    readme_path = repo / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        readme = re.sub(r"Original bytes: [0-9,]+", f"Original bytes: {len(rebuilt):,}", readme)
        readme = re.sub(r"Original SHA-256: `[0-9a-f]{64}`", f"Original SHA-256: `{sha256(rebuilt)}`", readme)
        readme = readme.replace(
            "- This only changes how the HTML client is served: from a local `file://` URL to an HTTPS GitHub Pages URL. It **does not** bypass CORS restrictions on a resource-pack host, and therefore may not fix the resource-pack error.",
            "- The embedded client Wasm is patched to acknowledge required server resource packs without downloading/reloading them. Server-provided pack textures will not load; Hypixel may still reject this unofficial browser client.",
        )
        readme_path.write_text(readme, encoding="utf-8")

    # Verify the newly generated parts reconstruct exactly and the loader matches.
    verification = b"".join((repo / str(item["file"])).read_bytes() for item in part_files)
    if verification != rebuilt:
        raise SystemExit("Chunk integrity verification failed.")
    if f"const expectedBytes = {len(rebuilt)};" not in loader:
        raise SystemExit("Loader byte count does not match the reconstructed client.")
    print(json.dumps({
        "clientBytes": len(rebuilt),
        "clientSha256": sha256(rebuilt),
        "embeddedWasmCompressedBytes": len(compressed),
        "partCount": len(part_files),
        "parts": part_files,
    }, indent=2))


if __name__ == "__main__":
    main()
