#!/usr/bin/env python3
"""Manifest-driven slicer for image-generated 2D game UI asset sheets.

The script intentionally stays generic. It can cut manual rects or regular grids,
optionally remove a chroma background, trim alpha, fit into a fixed canvas, create
Cocos Creator .meta files, and emit a contact sheet for review.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import uuid
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit("Pillow is required. Install with: python -m pip install Pillow") from exc


def resolve(base: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else base / path


def directory_meta(directory_uuid: str) -> dict[str, Any]:
    return {
        "ver": "1.2.0",
        "importer": "directory",
        "imported": True,
        "uuid": directory_uuid,
        "files": [],
        "subMetas": {},
        "userData": {},
    }


def cocos_png_meta(display_name: str, image_uuid: str, width: int, height: int, *,
                   pixels_to_unit: int = 100, nine_slice: dict[str, int] | None = None) -> dict[str, Any]:
    # Use integer half-extents when the dimension is even (the common case for
    # checked-in sprite frames). Odd dimensions keep the .5 that Cocos expects.
    half_w = width // 2 if width % 2 == 0 else width / 2
    half_h = height // 2 if height % 2 == 0 else height / 2
    ns = nine_slice or {}
    return {
        "ver": "1.0.27",
        "importer": "image",
        "imported": True,
        "uuid": image_uuid,
        "files": [".json", ".png"],
        "subMetas": {
            "6c48a": {
                "importer": "texture",
                "uuid": f"{image_uuid}@6c48a",
                "displayName": display_name,
                "id": "6c48a",
                "name": "texture",
                "userData": {
                    "wrapModeS": "clamp-to-edge",
                    "wrapModeT": "clamp-to-edge",
                    "imageUuidOrDatabaseUri": image_uuid,
                    "isUuid": True,
                    "visible": False,
                    "minfilter": "linear",
                    "magfilter": "linear",
                    "mipfilter": "none",
                    "anisotropy": 0,
                },
                "ver": "1.0.22",
                "imported": True,
                "files": [".json"],
                "subMetas": {},
            },
            "f9941": {
                "importer": "sprite-frame",
                "uuid": f"{image_uuid}@f9941",
                "displayName": display_name,
                "id": "f9941",
                "name": "spriteFrame",
                "userData": {
                    "trimThreshold": 1,
                    "rotated": False,
                    "offsetX": 0,
                    "offsetY": 0,
                    "trimX": 0,
                    "trimY": 0,
                    "width": width,
                    "height": height,
                    "rawWidth": width,
                    "rawHeight": height,
                    "borderTop": int(ns.get("top", ns.get("borderTop", 0))),
                    "borderBottom": int(ns.get("bottom", ns.get("borderBottom", 0))),
                    "borderLeft": int(ns.get("left", ns.get("borderLeft", 0))),
                    "borderRight": int(ns.get("right", ns.get("borderRight", 0))),
                    "packable": True,
                    "pixelsToUnit": pixels_to_unit,
                    "pivotX": 0.5,
                    "pivotY": 0.5,
                    "meshType": 0,
                    "vertices": {
                        "rawPosition": [-half_w, -half_h, 0, half_w, -half_h, 0, -half_w, half_h, 0, half_w, half_h, 0],
                        "indexes": [0, 1, 2, 2, 1, 3],
                        "uv": [0, 1, 1, 1, 0, 0, 1, 0],
                        "nuv": [0, 1, 1, 1, 0, 0, 1, 0],
                        "minPos": [-half_w, -half_h, 0],
                        "maxPos": [half_w, half_h, 0],
                    },
                    "isUuid": True,
                    "imageUuidOrDatabaseUri": image_uuid,
                    "atlasUuid": "",
                },
                "ver": "1.0.12",
                "imported": True,
                "files": [".json"],
                "subMetas": {},
            },
        },
        "userData": {"type": "sprite-frame", "hasAlpha": True, "redirect": "f9941"},
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_cocos_meta(path: Path, display_name: str, image: Image.Image, pixels_to_unit: int,
                     nine_slice: dict[str, int] | None) -> None:
    meta_path = path.with_suffix(path.suffix + ".meta")
    # Preserve an existing UUID so re-running the slicer does not break scene
    # or prefab references to this asset. Only size/border/texture fields are
    # refreshed; the identity stays stable across regenerations.
    existing_uuid = None
    if meta_path.exists():
        try:
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            existing_uuid = prev.get("uuid")
        except (json.JSONDecodeError, OSError):
            existing_uuid = None
    write_json(meta_path, cocos_png_meta(
        display_name,
        existing_uuid or str(uuid.uuid4()),
        image.width,
        image.height,
        pixels_to_unit=pixels_to_unit,
        nine_slice=nine_slice,
    ))


def remove_chroma(img: Image.Image, config: dict[str, Any]) -> Image.Image:
    mode = config.get("mode", "none")
    if mode == "none":
        return img
    if mode != "chroma":
        raise ValueError(f"Unsupported backgroundRemoval.mode: {mode}")
    color = tuple(config.get("color", [0, 255, 0]))
    tolerance = int(config.get("tolerance", 70))
    softness = int(config.get("softness", 20))
    src = img.convert("RGBA")
    pixels = src.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = pixels[x, y]
            dist = math.sqrt((r - color[0]) ** 2 + (g - color[1]) ** 2 + (b - color[2]) ** 2)
            if dist <= tolerance:
                pixels[x, y] = (r, g, b, 0)
            elif softness > 0 and dist <= tolerance + softness:
                alpha = int(a * ((dist - tolerance) / softness))
                pixels[x, y] = (r, g, b, alpha)
    return src


def trim_alpha(img: Image.Image, padding: int) -> Image.Image:
    src = img.convert("RGBA")
    bbox = src.getchannel("A").getbbox()
    if not bbox:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(src.width, bbox[2] + padding)
    bottom = min(src.height, bbox[3] + padding)
    return src.crop((left, top, right, bottom))


def fit_canvas(img: Image.Image, config: dict[str, Any] | None) -> Image.Image:
    if not config:
        return img
    width = int(config["width"])
    height = int(config["height"])
    max_size = int(config.get("max", min(width, height)))
    src = img.convert("RGBA")
    if src.width == 0 or src.height == 0:
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ratio = min(max_size / src.width, max_size / src.height, 1)
    resized = src.resize((max(1, round(src.width * ratio)), max(1, round(src.height * ratio))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return canvas


def rect_from_asset(asset: dict[str, Any], index: int = 0) -> tuple[int, int, int, int]:
    if "rect" in asset:
        x, y, w, h = [int(v) for v in asset["rect"]]
        return x, y, x + w, y + h
    grid = asset["grid"]
    grid_rect = grid.get("rect")
    if grid_rect is None:
        grid_rect = [0, 0, grid["width"], grid["height"]]
    gx, gy, gw, gh = [int(v) for v in grid_rect]
    cols = int(grid["cols"])
    rows = int(grid["rows"])
    gap_x = int(grid.get("gapX", 0))
    gap_y = int(grid.get("gapY", 0))
    inset = int(grid.get("inset", 0))
    col = index % cols
    row = index // cols
    cell_w = (gw - gap_x * (cols - 1)) / cols
    cell_h = (gh - gap_y * (rows - 1)) / rows
    x = round(gx + col * (cell_w + gap_x)) + inset
    y = round(gy + row * (cell_h + gap_y)) + inset
    return x, y, round(x + cell_w) - inset, round(y + cell_h) - inset


def expand_assets(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for asset in manifest["assets"]:
        if "grid" not in asset:
            expanded.append(asset)
            continue
        count = int(asset["grid"].get("count", int(asset["grid"]["cols"]) * int(asset["grid"]["rows"])))
        names = asset.get("names") or []
        prefix = asset.get("namePrefix", "asset_")
        for index in range(count):
            item = dict(asset)
            item.pop("names", None)
            left, top, right, bottom = rect_from_asset(asset, index)
            item["rect"] = [left, top, right - left, bottom - top]
            item["name"] = names[index] if index < len(names) else f"{prefix}{index + 1:02d}"
            item["out"] = item.get("outPattern", "{name}.png").format(name=item["name"], index=index + 1)
            expanded.append(item)
    return expanded


def validate_rect(rect: tuple[int, int, int, int], sheet: Image.Image, name: str) -> None:
    left, top, right, bottom = rect
    if left < 0 or top < 0 or right > sheet.width or bottom > sheet.height or right <= left or bottom <= top:
        raise ValueError(f"Invalid rect for {name}: {rect}, source size={sheet.size}")


def make_contact(images: list[tuple[str, Image.Image]], path: Path) -> None:
    if not images:
        return
    cell_w = max(120, max(img.width for _, img in images) + 28)
    cell_h = max(120, max(img.height for _, img in images) + 44)
    cols = min(5, max(1, math.ceil(math.sqrt(len(images)))))
    rows = math.ceil(len(images) / cols)
    contact = Image.new("RGBA", (cell_w * cols, cell_h * rows), (18, 22, 26, 255))
    draw = ImageDraw.Draw(contact)
    for i, (name, img) in enumerate(images):
        col = i % cols
        row = i // cols
        x = col * cell_w
        y = row * cell_h
        contact.alpha_composite(img, (x + (cell_w - img.width) // 2, y + 8))
        draw.text((x + 8, y + cell_h - 26), name[:28], fill=(230, 230, 220, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    contact.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    base = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = resolve(base, manifest["source"])
    if source is None:
        raise SystemExit("Manifest requires a source path.")
    output_dir = resolve(base, manifest.get("outputDir")) or (base / "runtime_slices")
    output_dir.mkdir(parents=True, exist_ok=True)

    defaults = manifest.get("defaults", {})
    bg_config = manifest.get("backgroundRemoval", {"mode": "none"})
    sheet = Image.open(source).convert("RGBA")
    produced: list[tuple[str, Image.Image]] = []
    records: list[dict[str, Any]] = []

    if defaults.get("cocosMeta", False):
        dir_meta_path = Path(str(output_dir) + ".meta")
        dir_uuid = None
        if dir_meta_path.exists():
            try:
                dir_uuid = json.loads(dir_meta_path.read_text(encoding="utf-8")).get("uuid")
            except (json.JSONDecodeError, OSError):
                dir_uuid = None
        write_json(dir_meta_path, directory_meta(dir_uuid or str(uuid.uuid4())))

    for asset in expand_assets(manifest):
        name = asset["name"]
        try:
            rect = rect_from_asset(asset)
            validate_rect(rect, sheet, name)
            image = sheet.crop(rect).convert("RGBA")
            image = remove_chroma(image, asset.get("backgroundRemoval", bg_config))
            nine = asset.get("nineSlice", defaults.get("nineSlice"))
            want_trim = asset.get("trim", defaults.get("trim", False))
            want_fit = asset.get("fit", defaults.get("fit"))
            if nine and want_trim:
                raise ValueError("nineSlice assets cannot use trim. Trimming shifts the border rectangle.")
            if nine and want_fit:
                raise ValueError("nineSlice assets cannot use fit. fit does not rescale the border rectangle; resize upstream or set fit on a non-sliced variant.")
            if want_trim:
                image = trim_alpha(image, int(asset.get("padding", defaults.get("padding", 0))))
            image = fit_canvas(image, want_fit)
        except (ValueError, KeyError) as exc:
            raise SystemExit(f"Invalid asset \"{name}\": {exc}") from exc

        out_rel = asset.get("out", f"{name}.png")
        out_path = output_dir / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(out_path)
        if asset.get("cocosMeta", defaults.get("cocosMeta", False)):
            write_cocos_meta(
                out_path,
                name,
                image,
                int(asset.get("pixelsToUnit", defaults.get("pixelsToUnit", 100))),
                nine,
            )
        produced.append((name, image))
        records.append({
            "name": name,
            "source": str(source),
            "rect": [rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]],
            "out": str(out_path),
            "size": [image.width, image.height],
            "nineSlice": nine,
        })

    contact = resolve(base, manifest.get("contactSheet"))
    if contact:
        make_contact(produced, contact)
    runtime_manifest = output_dir / "runtime_assets_manifest.json"
    write_json(runtime_manifest, {"source": str(source), "assets": records})
    print(f"Sliced {len(records)} assets to {output_dir}")
    if contact:
        print(f"Contact sheet: {contact}")
    print(f"Runtime manifest: {runtime_manifest}")


if __name__ == "__main__":
    main()
