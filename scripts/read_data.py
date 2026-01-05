"""
Complete script for reading data files and writing them to a single database.
"""

import sys
from pathlib import Path

this_path: Path = Path(__file__)
if (pkg_path := this_path.parents[1]) not in sys.path:
    sys.path.append(str(pkg_path))

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(
        'read_data',
        description = 'reads data files and writes them into a single database',
    )
    parser.add_argument(
        '-p', '--path_to_data',
        required = True,
        type = str,
    )
    parser.add_argument(
        '-n', '--name',
        required = False,
        default = 'db',
        type = str,
    )
    parser.parse_args()

    path_to_data: Path = Path(parser.path_to_data)
    name: str = parser.name