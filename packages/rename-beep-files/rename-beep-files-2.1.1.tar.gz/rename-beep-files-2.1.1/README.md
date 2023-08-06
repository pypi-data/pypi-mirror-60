
# Rename Beep File
This script is useful to rename all files inside a folder.     
Indeed it replaces all the instances of a target string (`target`) in the base name of each file with the character specified (`char`).


![GitHub release (latest by date)](https://img.shields.io/github/v/release/mett96/rename-beep-files)
![PyPI](https://img.shields.io/pypi/v/rename-beep-files?color=gre&logoColor=green)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rename-beep-files)
![GitHub stars](https://img.shields.io/github/stars/mett96/rename-beep-files?style=social)

The default values are:
* target = `+`
* char = ` ` (space character)

It is a very simple tool but very useful when directly downloading zip files from folders from the [Beep site](https://beep.metid.polimi.it). But its usage can be extended.
## Instructions
Install the script.
```bash
pip install rename-beep-files
```

Use it in the terminal
```bash
rename-beep-file
```

You may include several options:
* recursive
* target
* char 
* folder path

```bash
$ rename-beep-files -h   
usage: rename-beep-files [-h] [-r] [-t TARGET] [-c CHAR] [paths [paths ...]]

Process renames all the file into the target directory.

positional arguments:
  paths                 Specify all the folders in which execute the renaming

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       Execute the rename action recursively into all
                        subdirectories of targeted folder
  -t TARGET, --target TARGET
                        Specify the character to replace
  -c CHAR, --char CHAR  Specify the character with which you want to replace

```
