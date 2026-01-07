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

    print("Initialising database:")

    parser = ArgumentParser(
        'init_db',
        description = 'reads data files and writes them into a single database',
    )
    parser.add_argument(
        '--name',
        required = False,
        default = 'db',
        type = str,
        help = 'desired name of the database',
    )
    parser.add_argument(
        '--rec_case',
        required = False,
        default = None,
        choices = (None, 'A', 'B'),
        help = 'desired recombination case',
    )
    parser.add_argument(
        '--data_types',
        nargs = '*',
        required = False,
        default = None,
        help = 'desired data types',
    )
    parser.add_argument(
        '--z_bounds',
        nargs = 2,
        default = (1, 100),
        help = 'lower and upper bounds on Z (both inclusive)'
    )
    parser.add_argument(
        '--replace',
        action = 'store_true',
        help = 'whether to replace the previous database with the same name'
    )
    args = parser.parse_args()

    print(f"> Parsed: {args}")

    # The current file
    this_file: Path = Path(__file__)

    data_dir: Path = this_file.parents[1] / 'VI_64'
    assert data_dir.exists()
    
    n_files: int = len(list(data_dir.iterdir()))
    if n_files == 0:
        raise FileNotFoundError(
            f"No data files found in the 'VI_64' directory!"
        )
    
    print("> Found data files in 'VI_64'.")
    
    # Creating the dataframes
    from src.utils.writing import create_dataframes
    dataframes = create_dataframes(
        data_dir,
        rec_case = args.rec_case,
        data_types = args.data_types,
        z_bounds = args.z_bounds,
    )
    
    print("> Created dataframes.")

    # Create connection to db
    from src.utils.writing import connect_to_db
    _, connection = connect_to_db(
        name = args.name,
        replace = args.replace,
    )

    print("> Connected to the database.")

    # Write dataframes to db
    from src.utils.writing import write_dfs_to_db
    write_dfs_to_db(
        dataframes,
        connection,
        if_exists = 'append', # Appends to the initialised database
    )

    print("> Wrote the data onto the database.")

    print("> Success! Finished initialising database.")