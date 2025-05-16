#!/usr/bin/env python3
import logging
from argparse import ArgumentParser
from pathlib import Path
from re import match as re_match
from shutil import copy, copytree
from sys import exit as sys_exit
from tempfile import TemporaryDirectory
from zipfile import ZipFile

logging.basicConfig(level=logging.INFO, format='%(message)s')

def find_cbz_files(directory):
    """Find all .cbz files in the given directory."""
    return sorted(Path(directory).glob('*.cbz'))

def parse_volume_from_filename(filename):
    """Extract manga title and volume number from filename, ignoring chapter info."""
    # Improved pattern: extract main title, ignore chapter, get volume
    # Examples: Frieren_Ch1_v1, Demon_Slayer_Ch2_v1, Naruto, JoJo Volume 1
    pattern = r'(?i)^(?P<title>[\w\s\-\.]+?)(?:[ _.-]+ch\d+)?[ _.-]+v(?:ol(?:ume)?)?[ ._-]*(?P<vol>\d+)'  # title, optional chapter, volume
    regex_match_result = re_match(pattern, filename)
    if regex_match_result:
        title = regex_match_result.group('title').strip(' _.-')
        vol = regex_match_result.group('vol').lstrip('0') or '0'
        return title, vol
    return None, None

def group_cbz_by_volume(cbz_files):
    """Group CBZ files by detected volume, combining all chapters for the same manga and volume."""
    grouped = {}
    for cbz in cbz_files:
        title, vol = parse_volume_from_filename(cbz.stem)
        if title and vol:
            key = (title, vol)
            grouped.setdefault(key, []).append(cbz)
    return grouped

def list_compatible_files(grouped):
    if not grouped:
        logging.error('No compatible CBZ files with volume patterns found.')
        sys_exit(1)
    logging.info('Compatible CBZ files grouped by volume:')
    for (title, vol), files in grouped.items():
        logging.info(f'  {title} Volume {vol}:')
        for f in files:
            logging.info(f'    {f.name}')

def extract_cbz_to_temp(cbz_files, temp_dir):
    """Extract all CBZ files to a temp directory, organized by volume."""
    extracted = {}
    for (title, vol), files in cbz_files.items():
        vol_dir = Path(temp_dir) / f'{title}_Volume_{vol}'
        vol_dir.mkdir(parents=True, exist_ok=True)
        for cbz in files:
            with ZipFile(cbz, 'r') as zip_ref:
                chapter_dir = vol_dir / cbz.stem
                chapter_dir.mkdir(exist_ok=True)
                zip_ref.extractall(chapter_dir)
        extracted[(title, vol)] = vol_dir
    return extracted

def create_cbz_from_dir(output_path, input_dir):
    """Create a CBZ file from the contents of a directory, flattening all images."""
    with ZipFile(output_path, 'w') as zipf:
        files = [f for f in sorted(input_dir.rglob('*')) if f.is_file()]
        for idx, file in enumerate(files, 1):
            ext = file.suffix
            zipf.write(file, f'{idx:04d}{ext}')

def main():
    parser = ArgumentParser(description='CBZ Manager: Combine and manage CBZ files by volume.')
    parser.add_argument('--input', type=Path, default=Path.cwd(), metavar='INPUT_DIR', help='Directory to search for CBZ files. Defaults to the current working directory.')
    parser.add_argument('--output', type=Path, default=Path.cwd(), metavar='OUTPUT_DIR', help='Directory to save processed CBZ files. Defaults to the current working directory.')
    parser.add_argument('--all', action='store_true', help='Combine all chapters into a single CBZ file, ignoring volumes.')
    args = parser.parse_args()

    in_dir = args.input.resolve()
    out_dir = args.output.resolve()

    out_dir.mkdir(parents=True, exist_ok=True)

    cbz_files = find_cbz_files(in_dir)
    grouped = group_cbz_by_volume(cbz_files)
    list_compatible_files(grouped)

    with TemporaryDirectory() as temp_dir:
        extracted_data = extract_cbz_to_temp(grouped, temp_dir)
        if args.all:
            combined_dir = Path(temp_dir) / 'ALL_COMBINED'
            combined_dir.mkdir(exist_ok=True)
            for vol_path_data in extracted_data.values():
                for item in vol_path_data.iterdir():
                    if item.is_file():
                        copy(item, combined_dir / item.name)
                    elif item.is_dir():
                        copytree(item, combined_dir / item.name, dirs_exist_ok=True)
            out_name = None
            if grouped:
                (title, _), *_ = grouped.keys()
                out_name = f'{title}.cbz'
            else:
                first_file = next(iter(cbz_files), None)
                if first_file:
                    out_name = f'{first_file.stem.split("_")[0]}_Combined.cbz'
                else:
                    out_name = 'Combined.cbz'

            create_cbz_from_dir(out_dir / out_name, combined_dir)
            logging.info(f'Created combined CBZ: {out_dir / out_name}')
        else:
            for (title, vol), vol_path in extracted_data.items():
                out_name = f'{title}_Volume_{vol}.cbz'
                create_cbz_from_dir(out_dir / out_name, vol_path)
                logging.info(f'Created CBZ for {title} Volume {vol}: {out_dir / out_name}')
    logging.info('Temporary files cleaned up.')

if __name__ == '__main__':
    main()
