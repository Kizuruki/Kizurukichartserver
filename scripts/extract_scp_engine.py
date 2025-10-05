"""
SCP Engine Extractor - Multi-SCP Support

Requirements:
- Pillow
"""

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from PIL import Image

add_to_description = "Archived (read-only) file from Chart Cyanvas by Nanashi.\n"


def extract_file(zf: zipfile.ZipFile, src: str, dst: Path):
    """Extract a file from the zip to a destination path."""
    with zf.open(src.lstrip("/")) as f_src, open(dst, "wb") as f_dst:
        shutil.copyfileobj(f_src, f_dst)


def convert_to_png(src: Path, dst: Path):
    """Convert an image to PNG."""
    with Image.open(src) as img:
        img.convert("RGBA").save(dst, "PNG")


def save_json(data: dict, dst: Path):
    """Save dictionary as JSON file."""
    dst.write_text(json.dumps(data, indent=4), encoding="utf-8")


def process_resource(
    zf: zipfile.ZipFile, resource: dict, resource_type: str, out_root: Path
):
    """Process a single resource into a folder with JSON and files."""
    name = resource["name"]
    if f"/sonolus/{resource_type}s/{name}" in zf.namelist():
        with zf.open(f"/sonolus/{resource_type}s/{name}") as f:
            resource_expanded_data = json.load(f)
    else:
        resource_expanded_data = {}
    folder_name = f"{resource_type}_{name}"
    res_dir = out_root / folder_name
    if res_dir.exists():
        return res_dir  # Skip already extracted
    res_dir.mkdir(parents=True, exist_ok=True)

    # Resource JSON
    res_json = {
        "version": resource["version"],
        "title": resource["title"],
        "subtitle": resource.get("subtitle", ""),
        "author": resource.get("author", ""),
    }
    if resource.get("description"):
        res_json["description"] = resource["description"]
        res_json["description"] = f"{add_to_description}\n{res_json['description']}"
    elif resource_expanded_data.get("description"):
        res_json["description"] = resource_expanded_data["description"]
        res_json["description"] = f"{add_to_description}\n{res_json['description']}"
    elif len(add_to_description.strip()) != 0:
        res_json["description"] = add_to_description
    save_json(res_json, res_dir / f"{resource_type}.json")

    # Extract files
    for key, value in resource.items():
        if isinstance(value, dict) and "url" in value:
            url = value["url"]
            if key == "thumbnail":
                extract_file(zf, url, res_dir / f"{key}.png")
            elif key == "configuration":
                extract_file(zf, url, res_dir / f"{key}.json.gz")
            elif key == "image" and resource_type == "background":
                # Convert background image to PNG
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                extract_file(zf, url, tmp_path)
                convert_to_png(tmp_path, res_dir / f"{key}.png")
                tmp_path.unlink(missing_ok=True)
            else:
                extract_file(zf, url, res_dir / key)
    return res_dir


def extract_engine(scp_path: Path, out_root: Path):
    """Extract engine and all resources from a single SCP file."""
    out_root.mkdir(exist_ok=True)

    with zipfile.ZipFile(scp_path, "r") as zf:
        try:
            with zf.open("sonolus/engines/list") as f:
                engine_list = json.load(f)
        except KeyError:
            print(f"No engines found in {scp_path}")
            return

        engine = engine_list["items"][0]

        if f"sonolus/engines/{engine['name']}" in zf.namelist():
            with zf.open(f"sonolus/engines/{engine['name']}") as f:
                engine_expanded_data = json.load(f)
        else:
            engine_expanded_data = {}

        engine_dir = out_root / engine["name"]
        engine_dir.mkdir(parents=True, exist_ok=True)

        engine_json = {
            "version": engine["version"],
            "title": engine["title"],
            "subtitle": engine.get("subtitle", ""),
            "author": engine.get("author", ""),
            "skin_name": engine["skin"]["name"],
            "background_name": engine["background"]["name"],
            "effect_name": engine["effect"]["name"],
            "particle_name": engine["particle"]["name"],
        }
        if engine.get("description"):
            engine_json["description"] = engine["description"]
            engine_json["description"] = (
                f"{add_to_description}\n{engine_json['description']}"
            )
        elif engine_expanded_data.get("description"):
            engine_json["description"] = engine_expanded_data["description"]
            engine_json["description"] = (
                f"{add_to_description}\n{engine_json['description']}"
            )
        elif len(add_to_description.strip()) != 0:
            engine_json["description"] = add_to_description
        save_json(engine_json, engine_dir / "engine.json")

        # Top-level engine files
        top_keys = [
            "thumbnail",
            "playData",
            "watchData",
            "previewData",
            "tutorialData",
            "configuration",
        ]
        for key in top_keys:
            if key in engine:
                url = engine[key]["url"]
                if key == "thumbnail":
                    extract_file(zf, url, engine_dir / f"{key}.png")
                elif key == "configuration":
                    extract_file(zf, url, engine_dir / f"{key}.json.gz")
                else:
                    extract_file(zf, url, engine_dir / key)

        # --- Resources from SCP lists ---
        for resource_type_plural in ["skins", "backgrounds", "effects", "particles"]:
            list_path = f"sonolus/{resource_type_plural}/list"
            try:
                with zf.open(list_path) as f:
                    res_list = json.load(f)
            except KeyError:
                continue
            type_name = resource_type_plural[:-1]  # skins -> skin
            for res_item in res_list["items"]:
                process_resource(zf, res_item, type_name, engine_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Extract engines and resources from SCP files."
    )
    parser.add_argument("scp_files", type=Path, nargs="+", help="One or more SCP files")
    parser.add_argument(
        "--out", type=Path, default=Path("extracted_engine"), help="Output folder"
    )
    args = parser.parse_args()

    for scp_path in args.scp_files:
        extract_engine(scp_path, args.out)

    print("All done.")


if __name__ == "__main__":
    main()
