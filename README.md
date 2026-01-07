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
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About

Lorem ipsum...

## Getting Started

How to clone the project:

```bash
git clone https://github.com/liamdeburca/PySH1995.git
```

In order to create the main database, the code needs to access a directory of gzipped files from **SH1995**. Currently (January 2026) this can be done following these steps:

1. Go to: https://cdsarc.cds.unistra.fr/ftp/cats/VI/64/
2. Click on *tar.gz*.
3. Unpacking the *tar.gz* file creates a *VI_64* folder which is used.


### Prerequisites

```bash
example-tool >= 1.2.3
```

## Usage

Where and how to download data from SH1995. 
How to initialise the primary database.
How to interact with scripts and pipelines.

## Contributing

This is (was) a small side project of mine, and it will likely stay so. If you find the tools especially helpful and would like to contribute, please contact me. 

## License

(No license)

## Acknowledgements


- Storey, P. J., & Hummer, D. G. (1995). *Recombination line intensities for hydrogenic ions IV: Total recombination coefficients and machine-readable tables for Z = 1–8*. Monthly Notices of the Royal Astronomical Society, 272(1), 41–48. https://doi.org/10.1093/mnras/272.1.41
