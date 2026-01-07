"""
PhysicalState class.
"""
from typing import Literal, Optional
from dataclasses import dataclass
from pandas import DataFrame

from .data_block import DataBlock

@dataclass
class PhysicalState:
    rec_case: Literal['A', 'B']
    z: int
    n_c: Optional[int] = None

    data_blocks: Optional[list] = None

    @staticmethod
    def from_lines(
        lines: list[str], 
        data_type: Literal['emi', 'rec', 'opa', 'dep'],
    ) -> 'PhysicalState':

        hdr: list[str] = lines[1].strip().split()
        z:        int = int(hdr[1])
        rec_case: str = hdr[3]
        n_c:      int = int(hdr[4])
        
        physical_state = PhysicalState(
            z, rec_case,
            n_c = n_c,
        )
        _lines: list[str] = None

        match data_type:
            case 'emi': dtype = 'E'
            case 'rec': dtype = 'R'
            case 'opa': dtype = 'A'
            case 'dep': dtype = 'B'
        
        idx: int = 2
        while True:
            if idx >= len(lines): break

            line = lines[idx]

            if _lines is None:
                # No current group of lines selected    
                if (line.strip()[0].upper() == dtype) \
                    and not (line.strip().startswith('BNS')):
                    _lines = [line]

                idx += 1
                continue

            else:
                # Current group of lines selected
                if line.strip()[0].isalpha():
                    # End current block, reset group of lines, repeat
                    block = DataBlock.from_lines(_lines)

                    if physical_state.data_blocks is None:
                        physical_state.data_blocks = []

                    physical_state.data_blocks.append(block)
                    _lines = None

                    continue

                _lines.append(line)
                idx += 1
                continue

        return physical_state
    
    def getStats(
        self,
    ) -> dict[tuple[float, float], dict[tuple[int, int], float]]:
        """
        Sums 
        """
        from collections import defaultdict

        assert self.data_blocks is not None

        self._stats: dict[tuple[float, float], dict[tuple[int, int], float]] = \
            defaultdict(lambda: {})

        for dblock in self.data_blocks:
            key1 = (dblock.temp, dblock.dens)
            for nl, stat in zip(dblock.nls, dblock.data):
                key2 = (dblock.n_u, nl)
                self._stats[key1][key2] = stat

        return self._stats
    
    def getSpecificStat(
        self,
        td: tuple[float, float],
        transition: tuple[int, int],
        stats: Optional[dict] = None,
    ) -> float:
        
        if stats is None:
            if not hasattr(self, '_stats'):
                _ = self.getStats()
            stats = self._stats

        return stats[td][transition]
    
    def toDict(self) -> dict:
        """
        Returns a dictionary containing this instance's data.
        """
        from collections import defaultdict

        assert self.data_blocks is not None

        d = defaultdict(lambda: [])
        for dblock in self.data_blocks:
            _ = dblock.appendToDict(d)

        return d
    
    def toDataFrame(self) -> DataFrame:
        """
        Returns a DataFrame containing this instance's data.
        """
        from pandas import DataFrame

        assert self.data_blocks is not None

        return DataFrame(self.toDict())