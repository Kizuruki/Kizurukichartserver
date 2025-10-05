"""
Compile extracted level folders into individual zip files.

requirements:
- Python 3.8+
"""

prefix = "UnCh"

import shutil
from pathlib import Path
import argparse
import uuid


def zip_folder(folder: Path, output_dir: Path, prefix: str):
    """Zip a folder and name it {prefix}-{uuid4}.zip."""
    uid1 = str(uuid.uuid4()).replace("-", "")
    zip_name = f"{prefix}-{uid1}.zip"
    zip_path = output_dir / zip_name

    shutil.make_archive(str(zip_path.with_suffix("")), "zip", folder)
    shutil.rmtree(folder)  # delete original folder
    print(f"Zipped {folder.name} -> {zip_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Compile extracted level folders into zips."
    )
    parser.add_argument(
        "out_folder",
        type=Path,
        help="Path to the folder containing extracted level subdirs",
    )
    args = parser.parse_args()

    out_folder = args.out_folder
    if not out_folder.exists() or not out_folder.is_dir():
        print("Output folder does not exist or is not a directory.")
        return

    # Iterate through all subdirectories
    for subdir in [d for d in out_folder.iterdir() if d.is_dir()]:
        zip_folder(subdir, out_folder, prefix)

    print("All folders compiled.")


if __name__ == "__main__":
    main()
