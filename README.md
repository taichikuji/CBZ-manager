<p align="center">
  <img src="media/cbz.webp" alt="CBZ-manager Logo" width="150px"/>
  <br/>
  <img src="https://img.shields.io/github/license/taichikuji/CBZ-manager?logo=github" alt="License"/>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python Version"/>
</p>

<h1 align="center">CBZ-manager</h1>
<p align="center">A tool to decompress, compress, combine, CBZ individual files.</p>

---

# 🚀 Usage

1. **Download the project:**

   ```bash
   git clone https://github.com/taichikuji/CBZ-manager.git
   ```

2. **Run the script with the following available flags:**

   ```bash
   ./CBZ-manager.py [--all] [--input FOLDER_PATH] [--output FOLDER_PATH] [--title TITLE_NAME]
   ```

3. **Enjoy!**

---

# ⚙️ Explanation regarding flags

As you may have noticed, this tool supports certain optional flags. These flags are really useful to cater to your needs and specific configurations. Allow me to explain them briefly:

All flags can be used and intertwined between each other.

<table>
  <tr>
    <th>Flag</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>--all</code></td>
    <td>Optional flag that, when used, will combine all CBZ files into a single one.</td>
  </tr>
  <tr>
    <td><code>--input</code></td>
    <td>Set to manually define the location where the script will operate.</td>
  </tr>
  <tr>
    <td><code>--output</code></td>
    <td>Set to manually define the output location.</td>
  </tr>
  <tr>
    <td><code>--title</code></td>
    <td>Manually set a Title that will be used for the output.</td>
  </tr>
</table>

> **Note:**
> 
> By default if <code>--all</code> is not used, it will do a per-volume CBZ merge.
> 
> Per-volume will attempt to combine all chapters from a specific Title, from a specific Volume, and it will generate as many CBZ files as there are Volumes detected.

> **Note:**
> 
> By default CBZ-manager.py will choose the location where the script is located.

> **Note:**
> 
> By default, when <code>--title</code> is not set, it will attempt to detect and extract the title, however, this can cause issues of operation if the title is not consistent.
> 
> CBZ-manager.py expects consistency, and if certain files from the same Title / Manga / Comic are not called the same, even if slightly, it will proceed to separate it and treat it like a different Title / Manga / Comic.
> 
> When in doubt, use the <code>--title</code> flag to set it to the name you prefer.

---

# 📝 A note

The script expects something along these lines:

**Examples of filenames that SHOULD work:**

- `My Awesome Manga_v01.cbz` (Title: `My Awesome Manga`, Volume: `1`)
- `Series Title - Chapter 10 - vol 2.cbz` (Title: `Series Title`, Volume: `2`)
- `Another.Book.volume.003.cbz` (Title: `Another.Book`, Volume: `3`)
- `Manga Name_ch25_V04_Special.cbz` (Title: `Manga Name`, Volume: `4`)
- `Title with Spaces v 5.cbz` (Title: `Title with Spaces`, Volume: `5`)

The script on the contrary will function with `--all` flag, but most likely not properly.

**Examples of filenames that will LIKELY NOT work (or not as intended):**

- `My Awesome Manga Book 1.cbz` (Missing `v`, `vol`, or `volume` keyword)
- `Series Title - 02.cbz` (No clear volume keyword, just a number)
- `Another.Book.Three.cbz` (Volume number is a word, not digits)
- `Manga Name_04_ch25.cbz` (Volume number appears before chapter and without a `v` keyword)
- `JustATitle.cbz` (No volume information at all)

---

# 🤝 Contributing

We welcome contributions from the community! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

---

# 📦 Dependencies

- Python 3.12+

---