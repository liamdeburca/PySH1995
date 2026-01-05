"""
DataBlock class.
"""
from dataclasses import dataclass
import numpy as np

from ...custom_types import RecType, DataType

def parse_int(s: str) -> int:
    return int(s)

def parse_float(s: str) -> float:
    mantissa: str = s[:-4]
    pwr: str = s[-4:].removeprefix('E')
    return float(f"{mantissa}E{pwr}")

@dataclass
class DataBlock:
    dens: float
    temp: float

    z: int
    n_u: int
    rec_case: RecType
    data_type: DataType

    raw_data: list[str]  = None
    nls: np.ndarray[int]    = None
    data: np.ndarray[float] = None

    def __str__(self) -> str:
        return "DataBlock {}: {}_NU={}, Z={}, TE={}, NE={}, CASE={}" \
            .format(
                hex(id(self)),
                self.data_type,
                self.n_u,
                self.z,
                self.temp,
                self.dens,
                self.rec_case,
            )

    @staticmethod
    def from_lines(lines: list[str]) -> 'DataBlock':
        hdr: str = lines[0]

        hdr_elements: dict = {}
        for elem in hdr.replace('= ', '=').strip().split():
            key, val = elem.split('=')
            hdr_elements[key] = val

        dens: float = float(hdr_elements.pop('NE'))
        temp: float = float(hdr_elements.pop('TE'))

        z:        int = int(hdr_elements.pop('Z'))
        rec_case: str = hdr_elements.pop('CASE')

        match (_data_type := hdr_elements.popitem())[0].split('_')[0]:
            case 'E': data_type = 'emi' # Emissivities
            case 'R': data_type = 'rec' # Recombination coefficients
            case 'A': data_type = 'opa' # Opacity factors
            case 'B': data_type = 'dep' # Departure coefficients

        n_u: int = int(_data_type[1])

        return DataBlock(
            dens, temp, z, n_u, rec_case, data_type,
            raw_data = lines[1:],
        ).processRawData()
    
    @property
    def sorting_key(self) -> tuple[float]:
        return (
            self.data_type, self.rec_case, 
            self.z, self.n_u, 
            self.temp, self.dens,
        )

    def processRawData(self) -> 'DataBlock':
        """
        Each data point consists of 13 characters:
        - n_l:   3 characters
        - space: 1 character
        - valie: 9 characters
        """
        from numpy import array

        assert self.raw_data is not None

        nls:  list[int]   = []
        data: list[float] = []

        for line in self.raw_data:
            
            count: int = 0
            while True:
                sel = slice(
                    start := 1 + 13 * count,
                    start + 13,
                    1,
                )
                word: str = line[sel]

                if len(word) != 13: break

                nls.append(parse_int(word[:3]))
                data.append(parse_float(word[4:]))

                count += 1

        if not len(nls) == len(data):
            raise AssertionError(
                f"{len(nls)} = {len(data)} ({self.n_u=})"
            )

        self.nls: np.ndarray[int]    = array(nls, dtype=int)
        self.data: np.ndarray[float] = array(data, dtype=float)

        return self
    
    def toDict(self) -> dict:
        """
        Returns a dictionary containing this instance's data.
        """
        from collections import defaultdict

        assert self.data is not None

        return self.appendToDict(defaultdict(lambda: []))
    
    def appendToDict(self, d: dict) -> dict:
        """
        Appends the instance's data to a dictionary.
        """
        from itertools import repeat
        from ..funcs import calculateWave

        n: int = self.nls.size

        if self.data_type == 'emi':
            d['wave'].extend(calculateWave(nl, self.n_u, self.z) for nl in self.nls)

        d['rec_case'].extend(repeat(self.rec_case, n))
        d['z']       .extend(repeat(self.z, n))
        d['n_u']     .extend(repeat(self.n_u, n))
        d['n_l']     .extend(self.nls)
        d['temp']    .extend(repeat(self.temp, n))
        d['dens']    .extend(repeat(self.dens, n))
        d['val']     .extend(self.data)

        return d