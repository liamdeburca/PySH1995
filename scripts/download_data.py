"""
This script downloads, unpacks, and formats data necessary to create databases.

More specifically, it does the following:
1.  Empties the 'VI_64' directory.
2.  Downloads the archived data using a url. This data is written to a temporary
    file in the 'VI_64' directory.
3.  The downloaded tar file is unpacked into the 'VI_64' directory.
4.  The downloaded tar file is deleted. 
"""

CHUNK_SIZE: int = 8192

def get_description(
    n_chunks: int, 
    chunk_size: int = CHUNK_SIZE,
) -> str:
    
    if (n_bytes := n_chunks * chunk_size) > 1e9:
        unit = 'B'
        val = n_bytes / 1e9
    elif n_bytes > 1e6:
        unit = 'M'
        val = n_bytes / 1e6
    elif n_bytes > 1e3:
        unit = 'K'
        val = n_bytes / 1e3
    else:
        unit = ''
        val = n_bytes

    return f"{val:.1f}{unit} bytes written"

if __name__ == '__main__':
    import requests
    import tarfile

    from os import remove
    from pathlib import Path
    from tqdm import tqdm

    # The current file
    this_file: Path = Path(__file__)

    # The location of the output
    out_dir: Path = this_file.parents[1] / 'VI_64'
    
    # The tar file
    path_to_tar: Path = out_dir / 'VI_64.tar.gz'
    if path_to_tar.exists():
        remove(path_to_tar)

    # Clear the current output directory
    for child in out_dir.iterdir():
        remove(child)

    # Downloading the data
    url: str = 'https://cdsarc.cds.unistra.fr/viz-bin/nph-Cat/tar.gz?VI/64'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(path_to_tar, 'wb') as tar:
            pbar = tqdm(
                enumerate(r.iter_content(chunk_size=CHUNK_SIZE), start=1),
                leave = True,
            )
            pbar.set_description(get_description(0))
            for n_chunks, chunk in pbar:
                tar.write(chunk)
                pbar.set_description(get_description(n_chunks))

    # Extracting the archive
    with tarfile.open(path_to_tar, 'r') as tar:
        tar.extractall(path=out_dir, filter='data')

    # Deleting the downloaded data
    remove(path_to_tar)