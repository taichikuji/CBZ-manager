#!/usr/bin/env python3
from pathlib import Path
from argparse import ArgumentParser
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copy, copytree

from typing import Dict, List, Tuple, Optional


def extract_cbz_to_temp(
    cbz_files: Dict[Tuple[str, int, int], List[str]], temp_dir: Path
) -> Dict[Tuple[str, int], Path]:
    extracted = {}
    sorted_items = sorted(cbz_files.items(), key=lambda x: (x[0][0], x[0][2], x[0][1]))
    for (title, chapter, vol), files in sorted_items:
        vol_dir = Path(temp_dir) / f"{title}_Volume_{vol}"
        vol_dir.mkdir(parents=True, exist_ok=True)
        for cbz in files:
            with ZipFile(cbz, "r") as zip_ref:
                # print(f"[DEBUG] [EXTRACT] {cbz} -> {vol_dir}")
                chapter_dir = vol_dir / f"Chapter_{chapter:03d}"
                chapter_dir.mkdir(exist_ok=True)
                zip_ref.extractall(chapter_dir)
        extracted[(title, vol)] = vol_dir
    print(f"[INFO] Extracted {len(extracted)} volumes to temporary directory.")
    return extracted


def create_cbz_from_dir(output_path: Path, input_dir: Path) -> None:
    """Create a CBZ file from the contents of a directory."""
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipf:
        files = [f for f in sorted(input_dir.rglob("*")) if f.is_file()]
        for idx, file in enumerate(files, 1):
            # print(f"[DEBUG] [COMPRESS] {file} -> {idx}")
            ext = file.suffix
            zipf.write(file, f"{idx:04d}{ext}")
        print(f"[INFO] [COMPRESS] Created CBZ file: {output_path}")


def extract_info(
    filename: str, manual_title: Optional[str] = None
) -> Tuple[str, int, int]:
    base = Path(filename).stem
    volume_match = re.search(r"(?:vol(?:ume)?\.?\s*|v\.?\s*)(\d+)", base, re.IGNORECASE)
    volume = int(volume_match.group(1)) if volume_match else 1
    chapter_match = re.search(r"(?:ch(?:apter)?\.?\s*)(\d+)", base, re.IGNORECASE)
    chapter = int(chapter_match.group(1)) if chapter_match else 1
    if manual_title is not None:
        title = manual_title
    else:
        title_part = re.split(
            r"(?:vol(?:ume)?\.?\s*|v\.?\s*)\d+|(?:ch(?:apter)?\.?\s*)\d+",
            base,
            flags=re.IGNORECASE,
        )[0]
        title = title_part.strip("_ ").replace("_", " ").replace(".", " ").strip()
    return title, chapter, volume


def sort_files(files: List[str], manual_title: Optional[str] = None) -> List[str]:
    # sort per chapter, volume, then title
    return sorted(files, key=lambda x: extract_info(x, manual_title))


def process_files(
    files: List[str], manual_title: Optional[str] = None
) -> Dict[Tuple[str, int, int], List[str]]:
    # Important: This is where the sorting occurs and files are returned in correct order.
    # This means that whenever other functions will be called, they should use this order every time.
    sorted_files = sort_files(files, manual_title)
    organized = {}
    for file in sorted_files:
        info = extract_info(file, manual_title)
        organized[info] = organized.get(info, []) + [file]
        # print(f"[DEBUG] [PROCESS] {file} -> {info}")
    print(f"[INFO] [PROCESS] Sorted {len(organized)} CBZ files.")
    return organized


def combine_volumes(
    extracted: Dict[Tuple[str, int], Path], temp_dir: Path
) -> Path:
    """Combine all volumes into a single directory when using --all flag"""
    combined_dir = Path(temp_dir) / "ALL_COMBINED"
    combined_dir.mkdir(exist_ok=True)

    for vol_path in extracted.values():
        for item in vol_path.iterdir():
            if item.is_file():
                copy(item, combined_dir / item.name)
            elif item.is_dir():
                copytree(item, combined_dir / item.name, dirs_exist_ok=True)
    return combined_dir


def main() -> None:
    parser = ArgumentParser(description="CBZ file manager tool")
    parser.add_argument("--input", type=str, help="Input folder path", default=None)
    parser.add_argument("--output", type=str, help="Output folder path", default=None)
    parser.add_argument(
        "--title", type=str, help="Manually set the title for sorting", default=None
    )
    parser.add_argument(
        "--all", action="store_true", help="Combine all volumes into a single CBZ file"
    )
    args = parser.parse_args()

    try:
        input_path = Path(args.input or Path(__file__).parent).resolve()
        output_path = Path(args.output or input_path).resolve()
    except Exception as e:
        print(f"[ERROR] Unable to determine script directory: {e}")
        return

    print(
        f"[INFO] Attempting to run CBZ-manager with --input [{input_path}] | --output [{output_path}]"
    )

    files = list(Path(input_path).glob("*.cbz"))
    if not files:
        print("[ERROR] Stopping. No CBZ files found.")
        return

    organized = process_files([str(f) for f in files], args.title)

    # Now that I have the variable sorted_files, I can unzip the files accordingly.
    # If --output folder is set, it will choose that.
    # Otherwise default input folder.
    with TemporaryDirectory() as temp_dir:
        extracted = extract_cbz_to_temp(organized, Path(temp_dir))
        out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        if args.all:
            combined_dir = combine_volumes(extracted, Path(temp_dir))

            if keys := list(organized.keys()):
                out_name = f"{keys[0][0]}.cbz"
            elif files:
                out_name = f'{Path(files[0]).stem.split("_")[0]}_Combined.cbz'
            else:
                out_name = "Combined.cbz"

            create_cbz_from_dir(out_dir / out_name, combined_dir)
        else:
            for (title, vol), vol_path in extracted.items():
                create_cbz_from_dir(out_dir / f"{title}_Volume_{vol}.cbz", vol_path)


if __name__ == "__main__":
    main()