#!/usr/bin/env python3

import sys
import glob
import os.path


def identify_i(i, datas):
    for j in range(0, i):
        if datas[i] == datas[j]:
            return j
    return i


def identify(datas):
    return [identify_i(i, datas) for i in range(len(datas))]


def flatten(list_of_lists):
    return [item for list_of_items in list_of_lists for item in list_of_items]


def split_bucket(chunk_size, bucket):
    ids = identify([f.read(chunk_size) for f in bucket])
    buckets = {}
    for i, bucket_index in enumerate(ids):
        buckets.setdefault(bucket_index, []).append(bucket[i])
    return list(buckets.values())


def join_if_same(size, files):
    fns = [open(file, 'rb') for file in files]
    buckets = [[f for f in fns]]
    size_left = size
    while size_left > 0:
        chunk_size = min(size_left, 1024)
        buckets = flatten([split_bucket(chunk_size, bucket) for bucket in buckets])
        size_left -= chunk_size
    buckets = [[f.name for f in bucket] for bucket in buckets if len(bucket) > 1]
    [f.close() for f in fns]
    return buckets


def resolve(bucket):
    rep = bucket[0]
    for f in bucket[1:]:
        os.remove(f)
        os.link(rep, f)


def sizeof_fmt(num, suffix="B"):
    """https://stackoverflow.com/a/1094933"""
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def main(path):
    print(f"find all files in '{path}' except symlinks (but including hardlinks) ...")
    files = glob.glob(os.path.join(path, "**/*"), recursive=True)
    files = [f for f in files if not os.path.islink(f) and os.path.isfile(f)]

    print(f"Found {len(files)} files.")
    print(f"Sort files by size ...")

    files_by_size = {}
    for file in files:
        stat = os.stat(file)
        # only keep one filename per inode
        files_by_size.setdefault(stat.st_size, {})[stat.st_ino] = file
    files_by_size = {size: list(files.values()) for size, files in files_by_size.items()}

    print("Find buckets of equal files ...")
    buckets = flatten([join_if_same(size, files) for size, files in files_by_size.items() if len(files) > 1])

    saved_size = 0
    for bucket in buckets:
        size = os.stat(bucket[0]).st_size
        saved_size += size * (len(bucket) - 1)
        if "--do" in sys.argv:
            resolve(bucket)
        else:
            print(bucket)

    print(f"Saved size: {sizeof_fmt(saved_size)}")


def has_help(argv):
    for arg in argv:
        if arg.lower() in ('--help', '-h', '?'):
            return True
    return False


if __name__ == "__main__":
    if len(sys.argv) > 3 or len(sys.argv) < 2 or has_help(sys.argv[1:]):
        print(f"Usage: {sys.argv[0]} DIRECTORY [--do]")
        print("Replace all identical files in DIRECTORY with hardlinks.")
        print("Omit the --do to do a dry run.")
        sys.exit(1)
    main(sys.argv[1])
