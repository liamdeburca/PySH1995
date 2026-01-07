# PySH1995

This small Python project containts methods, classes, and scripts suitable for working with data files from "Recombination line intensities for hydrogenuc ions - IV. Total recombination coefficients and machine-readable tables for Z=1 to 8" by P.J. Storey and D.G. Hummer (1995), hereafter **SH1995**. The article presents data files containing information useful for creating hydrogenic emission templates, specifically Balmer pseudo-continuum templates, which, in fact, motivated this project. The data files presented in this article are in an ASCII format, which by modern conventions (in my opinion) is archaic.

The aim of this project is therefore to provide the user with tools which allows them to easily begin extracting data, allowing them to more easily build templates (for example) of their own. 

## Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

## About

Lorem ipsum...

## Getting Started

How to clone the project:

```bash
git clone https://github.com/liamdeburca/PySH1995.git
```

Initialising the default database:

```bash
cd ../PySH1995
python scripts/default_setup.py
```

This will download the entire dataset from SH1995 and construct an SQL database containing emission, recombination, opacity, and departure values. Due to the size of the dataset, initial construction is fairly slow, and can be sped up by selecting which features to include in the database. 

### Prerequisites

```bash
python == 3.12
numpy == 1.26
pandas == 2.3
requests == 2.32
tqdm == 4.67
```

**Note**: older versions of these packages may still work. These are just the versions of the packages I used. 

## Usage

In most cases, the user should only need to use the Query class.

```python
from PySH1995 import Query

# Default database
name_of_database: str = 'db'
# Table of emissivities
name_of_table: str = 'emi'

with Query.START(name_of_database) as q:
    data = q.FROM(name_of_table)
            .SELECT('z', 'n_u', 'n_l', 'value')
            .WHERE('z == 1') 
            .WHERE('n_l == 1')
            .ORDER_BY('wave', descending=False)
            .LIMIT(100)
            .STOP()

    column_info = q.column_info
    table_names = q.table_names
    column_names = q.column_names

emissivities: list[float] = data['val']
```

## Contributing

This is (was) a small side project of mine, and it will likely stay so. If you find the tools especially helpful and would like to contribute, please contact me. 

## Acknowledgements


- Storey, P. J., & Hummer, D. G. (1995). *Recombination line intensities for hydrogenic ions IV: Total recombination coefficients and machine-readable tables for Z = 1–8*. Monthly Notices of the Royal Astronomical Society, 272(1), 41–48. https://doi.org/10.1093/mnras/272.1.41
