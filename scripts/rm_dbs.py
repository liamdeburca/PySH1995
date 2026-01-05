"""
Script for removing all generated databases stored in the 'databases' directory.
"""

import sys
from os import remove
from pathlib import Path

this_path: Path = Path(__file__)
if (pkg_path := this_path.parents[1]) not in sys.path:
    sys.path.append(str(pkg_path))

if __name__ == '__main__':
    from src.utils.writing import db_dir

    for db_path in db_dir.iterdir():
        if db_path.name == 'notes': continue

        print(f"Removing {db_path.name}")
        remove(db_path)