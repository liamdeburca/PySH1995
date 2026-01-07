"""
Script for removing all generated databases stored in the 'databases' directory.
Script for initialising a database in the 'databases' directory.
"""
import sys
from pathlib import Path

this_path: Path = Path(__file__)
if (pkg_path := this_path.parents[1]) not in sys.path:
    sys.path.append(str(pkg_path))

if __name__ == '__main__':
    from argparse import ArgumentParser
    from src.utils.writing import db_dir, initialise_db

    parser = ArgumentParser(
        prog = "mk_db",
        description = "Initialises a database.",
    )
    parser.add_argument(
        '--name',
        required = False,
        default = 'db',
        type = str,
        help = 'desired name of the database',
    )
    args = parser.parse_args()

    path_to_db: Path = db_dir / f"{args.name}.db"
    if path_to_db.exists():
        raise ValueError(f"Database with name '{args.name}' already exists!")
    else:
        _ = initialise_db(path_to_db)