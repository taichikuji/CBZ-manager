#!/usr/bin/env python3
from glob import glob
from pathlib import Path
from argparse import ArgumentParser
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_LZMA
from shutil import copy, copytree

def extract_cbz_to_temp(cbz_files, temp_dir):
    extracted = {}
    sorted_items = sorted(cbz_files.items(), key=lambda x: (x[0][0], x[0][2], x[0][1]))
    for (title, chapter, vol), files in sorted_items:
        vol_dir = Path(temp_dir) / f'{title}_Volume_{vol}'
        vol_dir.mkdir(parents=True, exist_ok=True)
        for cbz in files:
            with ZipFile(cbz, 'r') as zip_ref:
                chapter_dir = vol_dir / f'Chapter_{chapter:03d}'
                chapter_dir.mkdir(exist_ok=True)
                zip_ref.extractall(chapter_dir)
        extracted[(title, vol)] = vol_dir
    print(f"[INFO] Extracted {len(extracted)} volumes to temporary directory.")
    return extracted

def create_cbz_from_dir(output_path, input_dir):
    with ZipFile(output_path, 'w', compression=ZIP_LZMA, compresslevel=9) as zipf:
        files = [f for f in sorted(input_dir.rglob('*')) if f.is_file()]
        for idx, file in enumerate(files, 1):
            ext = file.suffix
            zipf.write(file, f'{idx:04d}{ext}')
        print(f"[INFO] Created CBZ file: {output_path}")

def extract_info(filename, manual_title=None):
    base = Path(filename).stem
    volume_match = re.search(r'(?:vol(?:ume)?\.?\s*|v\.?\s*)(\d+)', base, re.IGNORECASE)
    volume = int(volume_match.group(1)) if volume_match else 0
    chapter_match = re.search(r'(?:ch(?:apter)?\.?\s*)(\d+)', base, re.IGNORECASE)
    chapter = int(chapter_match.group(1)) if chapter_match else 0
    if manual_title is not None:
        title = manual_title
    else:
        title_part = re.split(r'(?:vol(?:ume)?\.?\s*|v\.?\s*)\d+|(?:ch(?:apter)?\.?\s*)\d+', base, flags=re.IGNORECASE)[0]
        title = title_part.strip('_ ').replace('_', ' ').replace('.', ' ').strip()
    return title, chapter, volume

def sort_files(files, manual_title=None):
    # sort per chapter, volume, then title
    return sorted(files, key=lambda x: extract_info(x, manual_title))

def main():
    parser = ArgumentParser(description='CBZ file manager tool')
    parser.add_argument('--input', type=str, help='Input folder path', default=None)
    parser.add_argument('--output', type=str, help='Output folder path', default=None)
    parser.add_argument('--title', type=str, help='Manually set the title for sorting, skipping title extraction', default=None)
    parser.add_argument('--all', action='store_true', help='Combine all volumes into a single CBZ file')
    args = parser.parse_args()
    
    try:
        script_dir = Path(__file__).parent.absolute()
        input_path = args.input if args.input else script_dir
        output_path = args.output if args.output else script_dir
    except:
        print("[ERROR] Unable to determine script directory.")
        return
    
    print(f"[INFO] CBZ-Manager.py executed with input path: {input_path} and output path: {output_path}")

    files = glob(str(Path(input_path).absolute() / "*.cbz"))
    
    if not files:
        print("No CBZ files found.")
        return
    
    # Important: This is where the sorting occurs and files are returned in correct order.
    # This means that whenever other functions will be called, they should use this order every time.
    sorted_files = sort_files(files, args.title)
    organized = {}
    for file in sorted_files:
        info = extract_info(file, args.title)
        organized[info] = organized.get(info, []) + [file]
    
    # Now that I have the variable sorted_files, I can unzip the files accordingly.
    # If --output folder is set, it will choose that.
    # Otherwise default input folder.
    with TemporaryDirectory() as temp_dir:
        extracted = extract_cbz_to_temp(organized, temp_dir)
        out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        if args.all:
            combined_dir = Path(temp_dir) / 'ALL_COMBINED'
            combined_dir.mkdir(exist_ok=True)
            for vol_path_data in extracted.values():
                for item in vol_path_data.iterdir():
                    if item.is_file():
                        copy(item, combined_dir / item.name)
                    elif item.is_dir():
                        copytree(item, combined_dir / item.name, dirs_exist_ok=True)
            out_name = None
            if organized:
                (title, _, _), *_ = organized.keys()
                out_name = f'{title}.cbz'
            else:
                first_file = Path(sorted_files[0]) if sorted_files else None
                if first_file:
                    out_name = f'{first_file.stem.split("_")[0]}_Combined.cbz'
                else:
                    out_name = 'Combined.cbz'

            create_cbz_from_dir(out_dir / out_name, combined_dir)
        else:
            for (title, vol), vol_path in extracted.items():
                out_name = f'{title}_Volume_{vol}.cbz'
                create_cbz_from_dir(out_dir / out_name, vol_path)

if __name__ == '__main__':
    main()
