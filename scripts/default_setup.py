"""
Default setup script. 

This will load and write all the data from SH1995, and is therefore much slower
than a custom setup pipeline tailored to your needs.
"""
import sys
from pathlib import Path

this_path: Path = Path(__file__)
if (pkg_path := this_path.parents[1]) not in sys.path:
    sys.path.append(str(pkg_path))

def main() -> None:
    from scripts import download_data, init_db

    download_data.main()
    init_db.main(init_db.DEFAULT_NAMESPACE)

if __name__ == '__main__':
    main()