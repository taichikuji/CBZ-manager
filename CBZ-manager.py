#!/usr/bin/env python3
import argparse
import logging
import re
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def find_cbz_files(directory):
    """Find all .cbz files in the given directory."""
    return sorted(Path(directory).glob('*.cbz'))

def parse_volume_from_filename(filename):
    """Extract manga title and volume number from filename, ignoring chapter info."""
    # Improved pattern: extract main title, ignore chapter, get volume
    # Examples: Frieren_Ch1_v1, Frieren_Ch2_v1, Frieren_v1, Frieren Volume 1
    pattern = r'(?i)^(?P<title>[\w\s\-\.]+?)(?:[ _.-]+ch\d+)?[ _.-]+v(?:ol(?:ume)?)?[ ._-]*(?P<vol>\d+)'  # title, optional chapter, volume
    match = re.match(pattern, filename)
    if match:
        title = match.group('title').strip(' _.-')
        vol = match.group('vol').lstrip('0') or '0'
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
        sys.exit(1)
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
                # Extract each file into a subfolder to avoid filename collisions
                chapter_dir = vol_dir / cbz.stem
                chapter_dir.mkdir(exist_ok=True)
                zip_ref.extractall(chapter_dir)
        extracted[(title, vol)] = vol_dir
    return extracted

def create_cbz_from_dir(output_path, input_dir):
    """Create a CBZ file from the contents of a directory, flattening all images."""
    with ZipFile(output_path, 'w') as zipf:
        # Flatten all files (images) from all subfolders, sorted
        files = [f for f in sorted(input_dir.rglob('*')) if f.is_file()]
        for idx, file in enumerate(files, 1):
            # Use a zero-padded index for ordering
            ext = file.suffix
            zipf.write(file, f'{idx:04d}{ext}')

def main():
    parser = argparse.ArgumentParser(description='CBZ Manager: Combine and manage CBZ files by volume.')
    parser.add_argument('--all', action='store_true', help='Combine all chapters into a single CBZ file, ignoring volumes.')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    cbz_files = find_cbz_files(script_dir)
    grouped = group_cbz_by_volume(cbz_files)
    list_compatible_files(grouped)

    with tempfile.TemporaryDirectory() as temp_dir:
        extracted = extract_cbz_to_temp(grouped, temp_dir)
        if args.all:
            # Combine all into one
            all_dir = Path(temp_dir) / 'ALL_COMBINED'
            all_dir.mkdir(exist_ok=True)
            for vol_dir in extracted.values():
                for item in vol_dir.iterdir():
                    if item.is_file():
                        shutil.copy(item, all_dir / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, all_dir / item.name, dirs_exist_ok=True)
            output_name = None
            if grouped:
                # Use the first title found
                (title, _), *_ = grouped.keys()
                output_name = f'{title}.cbz'
            else:
                output_name = 'Combined.cbz'
            create_cbz_from_dir(script_dir / output_name, all_dir)
            logging.info(f'Created combined CBZ: {output_name}')
        else:
            for (title, vol), vol_dir in extracted.items():
                output_name = f'{title}_Volume_{vol}.cbz'
                create_cbz_from_dir(script_dir / output_name, vol_dir)
                logging.info(f'Created CBZ for {title} Volume {vol}: {output_name}')
    logging.info('Temporary files cleaned up.')

if __name__ == '__main__':
    main()
