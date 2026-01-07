"""
Submodule containing utilities for writing data to a database.
"""
from typing import Optional, Iterator, Iterable, Literal
from pathlib import Path
from sqlite3 import Connection
from pandas import DataFrame

from ..custom_types import DataType, RecType

this_file: Path = Path(__file__)
db_dir: Path = this_file.parents[2] / 'databases'

def initialise_db(
    path: Path,
) -> Connection:
    """
    Initialises a databse.
    """
    from sqlite3 import connect

    assert not path.exists()

    connection = connect(path, timeout=0)
    c = connection.cursor()
    
    # Create 'emi' table
    c.execute("CREATE TABLE emi(wave, rec_case, z, n_u, n_l, temp, dens, val)")
    # Create 'rec' table
    c.execute("CREATE TABLE rec(wave, rec_case, z, n_u, n_l, temp, dens, val)")
    # Create 'opa' table
    c.execute("CREATE TABLE opa(wave, rec_case, z, n_u, n_l, temp, dens, val)")
    # Create 'dep' table
    c.execute("CREATE TABLE dep(wave, rec_case, z, n_u, n_l, temp, dens, val)")

    return connection

def connect_to_db(
    name: Optional[str] = None,
    replace: bool = False,
) -> tuple[Path, Connection]:
    """
    Connects to a database.

    If database doesn't already exist, one is created using a default name if
    none is explicitly provided.

    If database exists and 'replace' is True, it is reset.
    """
    from pathlib import Path
    from os import remove
    from sqlite3 import connect

    if name is None: name = 'db'
    else:            name = name.removesuffix('.db')

    path_to_db: Path = db_dir / f"{name}.db"
    if path_to_db.exists() and replace:
        # Removes the database and re-initialises it
        remove(path_to_db)
        connection = initialise_db(path_to_db)
    else:
        # Connects to the existing database
        connection = connect(path_to_db)

    return path_to_db, connection

def check_path(
    path: Path,
    rec_case: Optional[RecType] = None,
    z_bounds: tuple[int] = (1, 100),
) -> None:
    """
    Checks whether the path leads to a valid datafile, i.e. a datafile which is 
    compatible with parsing methods.

    Requirements:
    1. The file must exist.
    2. The file must be a gzipped datafile, i.e. end with '.d.gz'.
    3. The file name must be a primary output, i.e. name follows the rzcttt.d
       convention from Storey & Hummer (1995).
    """
    # 1.
    assert path.exists()

    fname = path.name

    # 2.
    assert (fname := path.name).endswith('.d.gz')

    # 3.
    assert fname.startswith('r') \
        and fname[1].isnumeric() \
        and fname[2].isalpha() \
        and fname[3:7].isnumeric()
    
    if rec_case is not None:
        assert (fname[2] == rec_case.lower())

    z = int(fname[1])
    assert (z_bounds[0] <= z) and (z <= z_bounds[1])
    
def path_is_valid(
    path: Path,
    rec_case: Optional[RecType] = None,
    z_bounds: tuple[int] = (1, 100),
) -> bool:
    """
    Checks the path returning True if all conditions are met.
    """
    try:
        check_path(path, rec_case=rec_case, z_bounds=z_bounds)
        return True
    except:
        return False

def unzip_and_read(
    path: Path,
) -> list[str]:
    """
    Reads a gzipped file returning all the file's lines.
    """
    import gzip

    with gzip.open(path, 'rb') as g:
        return [line.decode('ascii') for line in g.readlines()]
    
def read_datafiles(
    path: Path,
    rec_case: Optional[RecType] = None,
    z_bounds: tuple[int] = (1, 100),
) -> Iterator[list[str]]:
    """
    Scans through a directory's files and reads those which it identifies
    as data files. 

    Asserts
    -------
    The path exists.
    The path leads to a directory.
    """
    assert path.exists()
    assert path.is_dir()

    return (
        unzip_and_read(path_to_file) \
        for path_to_file \
        in path.iterdir() \
        if path_is_valid(path_to_file, rec_case=rec_case, z_bounds=z_bounds)
    )

def create_dataframes(
    path: Path,
    rec_case: Optional[RecType] = None,
    data_types: Optional[Iterable[DataType]] = None,
    z_bounds: tuple[int] = (1, 100),
) -> dict[DataType, DataFrame]:
    """
    Scans through a directory's files, reads them, and adds the data to Pandas
    DataFrames.
    """
    from collections import defaultdict
    from pandas import DataFrame

    from .parsing.physical_state import PhysicalState

    read_files_itr = read_datafiles(path, rec_case=rec_case, z_bounds=z_bounds)

    if data_types is None: data_types = {'emi', 'rec', 'opa', 'dep'}
    else:                  data_types = set(data_types)

    all_dicts: dict[str, dict] = {}
    for dtype in data_types:
        all_dicts[dtype] = defaultdict(lambda: [])
    
    # Read data
    for read_file in read_files_itr:
        for dtype in data_types:
            physical_state = PhysicalState.from_lines(
                read_file,
                data_type = dtype,
            )
            
            for dblock in physical_state.data_blocks:
                dblock.appendToDict(all_dicts[dtype])

    # Create dataframes
    all_dfs: dict[DataType, DataFrame] = dict(
        (
            dtype, 
            DataFrame(data).sort_values(['rec_case', 'z', 'n_l', 'n_u']),
        ) \
        for dtype, data \
        in all_dicts.items()
    )

    return all_dfs

def write_dfs_to_db(
    dataframes: dict[DataType, DataFrame],
    connection: Connection,
    if_exists: Literal['append', 'replace', 'fail'] = 'append',
) -> None:
    
    for table_name, df in dataframes.items():
        df.to_sql(
            table_name,
            connection,
            if_exists = if_exists,
            index = False,
        )