"""
SCP -> Level Folders

This script requires FFMPEG in your path!

requirements:
pillow
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from PIL import Image
import concurrent.futures

add_to_description = ""


def extract_file(zf: zipfile.ZipFile, src: str, dst: Path):
    """Extract a file from the zip to a given destination path."""
    with zf.open(src) as f_src, open(dst, "wb") as f_dst:
        shutil.copyfileobj(f_src, f_dst)


def convert_audio_to_mp3(src: Path, dst: Path):
    """Convert any audio file to mp3 using ffmpeg."""
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vn",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-b:a",
            "192k",
            str(dst),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def convert_image_to_png(src: Path, dst: Path):
    """Convert an image to PNG using Pillow."""
    with Image.open(src) as img:
        img.convert("RGBA").save(dst, "PNG")


def process_level(zf: zipfile.ZipFile, item: dict, out_root: Path, processed: set):
    level_name = item["name"]
    with zf.open(f"sonolus/levels/{level_name}") as f:
        level_expanded_data = json.load(f)
    level_dir = out_root / level_name

    # Skip if already processed
    if level_name in processed or level_dir.exists():
        print(f"Skipping {level_name}, already processed.")
        return False

    level_dir.mkdir(parents=True, exist_ok=True)

    # 1. level.json
    level_json = {
        "version": item.get("version"),
        "rating": item.get("rating"),
        "title": item.get("title"),
        "artists": item.get("artists"),
        "author": item.get("author"),
    }
    if item.get("description"):
        level_json["description"] = item["description"]
        level_json["description"] = f"{add_to_description}\n{level_json['description']}"
    elif level_expanded_data.get("description"):
        level_json["description"] = level_expanded_data["description"]
        level_json["description"] = f"{add_to_description}\n{level_json['description']}"
    elif len(add_to_description.strip()) != 0:
        level_json["description"] = add_to_description
    (level_dir / "level.json").write_text(
        json.dumps(level_json, indent=4), encoding="utf-8"
    )

    # 2. level.data
    data_url = item["data"]["url"].lstrip("/")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
    extract_file(zf, data_url, tmp_path)
    shutil.move(tmp_path, level_dir / "level.data")

    # 3. music.mp3
    bgm_url = item["bgm"]["url"].lstrip("/")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
    extract_file(zf, bgm_url, tmp_path)
    convert_audio_to_mp3(tmp_path, level_dir / "music.mp3")
    tmp_path.unlink(missing_ok=True)

    # 4. music_pre.mp3 (optional)
    if "preview" in item:
        preview_url = item["preview"]["url"].lstrip("/")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        extract_file(zf, preview_url, tmp_path)
        convert_audio_to_mp3(tmp_path, level_dir / "music_pre.mp3")
        tmp_path.unlink(missing_ok=True)

    # 5. jacket.png
    cover_url = item["cover"]["url"].lstrip("/")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
    extract_file(zf, cover_url, tmp_path)
    convert_image_to_png(tmp_path, level_dir / "jacket.png")
    tmp_path.unlink(missing_ok=True)

    # 6. stage & stage_thumbnail if useBackground.useDefault == False
    if not item.get("useBackground", {}).get("useDefault", True):
        bg_item = item["useBackground"]["item"]

        # stage.png
        image_url = bg_item["image"]["url"].lstrip("/")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        extract_file(zf, image_url, tmp_path)
        convert_image_to_png(tmp_path, level_dir / "stage.png")
        tmp_path.unlink(missing_ok=True)

        # stage_thumbnail.png
        thumb_url = bg_item["thumbnail"]["url"].lstrip("/")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        extract_file(zf, thumb_url, tmp_path)
        convert_image_to_png(tmp_path, level_dir / "stage_thumbnail.png")
        tmp_path.unlink(missing_ok=True)

    print(f"Processed {level_name}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Extract SCP(s) to multiple level folders."
    )
    parser.add_argument("scp", type=Path, nargs="+", help="Path(s) to .scp file(s)")
    args = parser.parse_args()

    out_root = Path("extracted_charts")
    out_root.mkdir(exist_ok=True)

    # Load processed.json if it exists
    processed_file = out_root / "processed.json"
    if processed_file.exists():
        with open(processed_file, "r", encoding="utf-8") as f:
            try:
                processed = set(json.load(f))
            except json.JSONDecodeError:
                processed = set()
    else:
        processed = set()

    updated = False
    for scp_path in args.scp:
        if not scp_path.exists():
            print(f"Warning: SCP file not found: {scp_path}")
            continue

        with zipfile.ZipFile(scp_path, "r") as zf:
            try:
                with zf.open("sonolus/levels/list") as f:
                    levels_data = json.load(f)
            except KeyError:
                print(f"Warning: No levels list found in {scp_path}")
                continue

            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
                # Map each item to a worker in the thread pool
                futures = [
                    executor.submit(process_level, zf, item, out_root, processed)
                    for item in levels_data["items"]
                ]

                # Iterate through the results after all threads have completed
                for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        updated = True

            for item in levels_data["items"]:
                if item["name"] not in processed:
                    processed.add(item["name"])

    # Save updated processed list
    if updated:
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(sorted(processed), f, indent=2)

    print("All done.")


if __name__ == "__main__":
    main()
