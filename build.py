"""build.py - validate a dsh-go pet pack (schema v1) and zip it.

Usage:
    python3 build.py            # generate sprites, validate, write the zip
    python3 build.py --check    # validate an existing set of PNGs only
"""

from __future__ import annotations

import json
import os
import sys
import zipfile

from PIL import Image

import gen_goku

ZIP_NAME = "goku-mui-pet.zip"
STATES = ["idle", "working", "thinking", "error", "success", "sleep"]


def validate(base="."):
    pack_path = os.path.join(base, "pack.json")
    if not os.path.exists(pack_path):
        raise FileNotFoundError("pack.json not found")

    with open(pack_path, "r", encoding="utf-8") as f:
        pack = json.load(f)

    assert pack.get("schema") == 1, "schema must be the integer 1"
    assert pack.get("scale") == 1, "scale must be 1"
    assert pack.get("canvas") == {"w": 300, "h": 300}, "canvas must be 300x300"

    preview = os.path.join(base, "preview.png")
    assert os.path.exists(preview), "preview.png is missing"
    with Image.open(preview) as im:
        assert im.size == (300, 300), f"preview.png must be 300x300, got {im.size}"

    anims = pack.get("animations", {})
    for state in STATES:
        assert state in anims, f"animation '{state}' missing from pack.json"
        a = anims[state]
        cols, fw, fh = a["cols"], a["frameW"], a["frameH"]
        assert len(a["frames"]) == cols, (
            f"'{state}' has {len(a['frames'])} frames but cols={cols}")
        for i, fr in enumerate(a["frames"]):
            assert 0 <= fr["i"] < cols, f"'{state}' frame {i} index out of range"
            assert fr["ms"] > 0, f"'{state}' frame {i} needs a positive ms"

        for folder in ("", "dark"):
            rel = os.path.join(folder, a["sheet"]) if folder else a["sheet"]
            path = os.path.join(base, rel)
            assert os.path.exists(path), f"{rel} not found"
            with Image.open(path) as im:
                want = (fw * cols, fh)
                assert im.size == want, f"{rel} is {im.size}, expected {want}"
                assert im.mode == "RGBA", f"{rel} must be RGBA, got {im.mode}"

    for state, targets in pack.get("states", {}).items():
        for t in targets:
            assert t in anims, f"state '{state}' -> unknown animation '{t}'"

    for name, target in pack.get("reactions", {}).items():
        assert target in anims, f"reaction '{name}' -> unknown animation '{target}'"

    # every animation frame must actually contain opaque pixels
    for state in STATES:
        a = anims[state]
        with Image.open(os.path.join(base, a["sheet"])) as sheet:
            for i in range(a["cols"]):
                box_ = (i * a["frameW"], 0, (i + 1) * a["frameW"], a["frameH"])
                frame = sheet.crop(box_)
                alpha = frame.getchannel("A")
                assert alpha.getbbox() is not None, (
                    f"{state} frame {i} is completely transparent")

    print(f"[validate] pack.json + {len(STATES) * 2} sprite sheets OK")


def build(base=".", zip_name=ZIP_NAME):
    print("[1/3] generating Goku MUI sprites (light + dark)...")
    gen_goku.generate_all(base)

    print("[2/3] validating schema v1 and sprite sheet dimensions...")
    validate(base)

    print(f"[3/3] packaging {zip_name}...")
    zip_path = os.path.join(base, zip_name)
    entries = [("pack.json", "pack.json"), ("preview.png", "preview.png")]
    for state in STATES:
        entries.append((f"{state}.png", f"{state}.png"))
        entries.append((os.path.join("dark", f"{state}.png"),
                        f"dark/{state}.png"))

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in entries:
            zf.write(os.path.join(base, src), arcname=arc)

    size = os.path.getsize(zip_path)
    print(f"done -> {zip_path} ({size / 1024:.1f} KB, {len(entries)} files)")


if __name__ == "__main__":
    if "--check" in sys.argv:
        validate(".")
    else:
        build()
