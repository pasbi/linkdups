# linkdups

A simple script to replace file duplicates with hard links.

The idea is to use this script to save a lot of space when creating backups:
Yesterday's backup is probably fairly similar to today's.
Instead of having uncontrolled redundancy on one fat system (i.e., one drive),
better have multiple lean copies of all your backups on multiple systems.


## Requirements

Obviously, only works on a filesystem that supports hardlinks.
Tested with Python 3.12, earlier Pythons (> 3.6) should be no problem.


## Usage

`main.py DIRECTORY --do`

Omit the `--do` to do a dry run: detect and print duplicates and the amount of potentially saved space without actually deleting files or creating new links.

For each file in DIRECTORY (recursively), it replaces all files that have identical content with hardlinks to that one file.
If a file is a symlink, it is untouched.

The script is fairly optimized and allows to process large amount of data and files.
