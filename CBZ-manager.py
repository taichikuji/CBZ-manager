#!/usr/bin/env python3
from glob import glob
from os import path
from argparse import ArgumentParser
import re

def extract_info(filename, manual_title=None):
    base = path.splitext(path.basename(filename))[0]
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
    args = parser.parse_args()
    
    try:
        script_dir = path.dirname(path.abspath(__file__))
        input_path = args.input if args.input else script_dir
        output_path = args.output if args.output else script_dir
    except:
        print("[ERROR] Unable to determine script directory.")
        return
    
    print(f"[INFO] Input path: {input_path}")
    print(f"[INFO] Output path: {output_path}")
    
    abs_input_path = path.abspath(input_path)
    search_path = path.join(abs_input_path, "*.cbz")
    files = glob(search_path)
    
    if not files:
        print("No CBZ files found.")
        return
    
    # Important: This is where the sorting occurs and files are returned in correct order.
    # This means that whenever other functions will be called, they should use this order every time.
    sorted_files = sort_files(files, args.title)
    print(f"[INFO] Found {len(sorted_files)} files, printing...")
    for file in sorted_files:
        print(f"{path.basename(file)}")

if __name__ == '__main__':
    main()
