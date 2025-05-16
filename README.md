# CBZ-manager
A tool to decompress, compress, combine, CBZ individual files.

# Usage

1. Download the project:

```
git clone https://github.com/taichikuji/CBZ-manager.git
```

2. Run the script with the following available flags:

```
./CBZ-manager.py [--all] [--input=FOLDER_PATH] [--output=FOLDER_PATH]
```

3. Enjoy!

# A note

The script expects something along these lines:

**Examples of filenames that SHOULD work:**

*   `My Awesome Manga_v01.cbz` (Title: `My Awesome Manga`, Volume: `1`)
*   `Series Title - Chapter 10 - vol 2.cbz` (Title: `Series Title`, Volume: `2`)
*   `Another.Book.volume.003.cbz` (Title: `Another.Book`, Volume: `3`)
*   `Manga Name_ch25_V04_Special.cbz` (Title: `Manga Name`, Volume: `4`)
*   `Title with Spaces v 5.cbz` (Title: `Title with Spaces`, Volume: `5`)

The script on the contrary will function with `--all` flag, but most likely not properly.

**Examples of filenames that will LIKELY NOT work (or not as intended):**

*   `My Awesome Manga Book 1.cbz` (Missing `v`, `vol`, or `volume` keyword)
*   `Series Title - 02.cbz` (No clear volume keyword, just a number)
*   `Another.Book.Three.cbz` (Volume number is a word, not digits)
*   `Manga Name_04_ch25.cbz` (Volume number appears before chapter and without a `v` keyword)
*   `JustATitle.cbz` (No volume information at all)