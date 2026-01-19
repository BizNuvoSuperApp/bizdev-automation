#!/usr/bin/env python

from pathlib import Path
from datetime import datetime, timedelta
import argparse

default_keep = 14
default_older_than = 14

def check_positive(value):
    try:
        ivalue = int(value)
    except ValueError:
        # Re-raise as ArgumentTypeError for argparse to handle nicely
        raise argparse.ArgumentTypeError(f"{value} is not an integer")

    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer (must be > 0)")
    return ivalue

def main(args):
    keep = args.keep if args.keep is not None else default_keep 
    older_than = (datetime.now() - timedelta(days=args.older_than if args.older_than is not None else default_older_than)).timestamp()

    sftp_dir = Path.home() / "sftp" / "downloads"
    branches = set()

    for file_path in sftp_dir.rglob('*'):
        if file_path.is_file():
            branches.add(file_path.name[8:][:-29])

    for branch in branches:
        print(f"Processing: {branch}")

        file_paths = [file_path for file_path in sftp_dir.rglob(f"*{branch}*") if file_path.is_file()]
        file_paths.sort(key=lambda path: path.stat().st_mtime, reverse=True)

        for index, file_path in enumerate(file_paths):
            if index >= keep and file_path.stat().st_mtime < older_than:
                print(f"delete {file_path.stat().st_mtime}\t{file_path.name}")
                file_path.unlink()
            else:
                print(f"keep {file_path.stat().st_mtime}\t{file_path.name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A rollover script for downloads.")
    parser.add_argument('-k', '--keep', type=check_positive, default=default_keep, help='How many files to keep')
    parser.add_argument('-o', '--older-than', type=check_positive, default=default_older_than, help='How many days older than today')
    args = parser.parse_args()

    print(f"Processing {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

    main(args)
