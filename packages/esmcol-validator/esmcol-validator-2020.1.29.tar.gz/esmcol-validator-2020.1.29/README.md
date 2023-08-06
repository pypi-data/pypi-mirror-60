[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NCAR/esmcol-validator/CI?logo=Github&style=for-the-badge)](https://github.com/NCAR/esmcol-validator/actions)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NCAR/esmcol-validator/code-style?label=Code%20Style&logo=GitHub&style=for-the-badge)](https://github.com/NCAR/esmcol-validator/actions)
[![PyPI](https://img.shields.io/pypi/v/esmcol-validator?logo=PyPI&style=for-the-badge)](https://pypi.org/project/esmcol-validator)
[![](https://img.shields.io/codecov/c/github/NCAR/esmcol-validator.svg?style=for-the-badge)](https://codecov.io/gh/NCAR/esmcol-validator)

# Earth System Model (ESM)Collection specification Validator

- [Earth System Model (ESM)Collection specification Validator](#earth-system-model-esmcollection-specification-validator)
  - [Installation](#installation)
  - [Usage](#usage)

This utility allows users to validate esm-collection json files against the [esm-collection-spec](https://github.com/NCAR/esm-collection-spec).

## Installation

The validator can be installed in any of the following ways:

Using Pip via PyPI:

```bash
python -m pip install esmcol-validator
```

Using Conda:

```bash
conda install -c conda-forge esmcol-validator
```

Or from the source repository:

```bash
python -m pip install git+https://github.com/NCAR/esmcol-validator.git
```

## Usage

```bash
$ esmcol-validator --help
Usage: esmcol-validator [OPTIONS] ESMCOL_FILE

  A utility that allows users to validate esm-collection json files against
  the esm-collection-spec.

Options:
  --esmcol-spec-dirs TEXT
  --version TEXT           [default: master]
  --verbose                [default: False]
  --timer                  [default: False]
  --log-level TEXT         [default: CRITICAL]
  --help                   Show this message and exit.
```

Example:

```bash
$ esmcol-validator sample-pangeo-cmip6-collection.json
{'collections': {'valid': 1, 'invalid': 0}, 'catalogs': {'valid': 1, 'invalid': 0}, 'unknown': 0}
{
    "collections": {
        "valid": 1,
        "invalid": 0
    },
    "catalogs": {
        "valid": 1,
        "invalid": 0
    },
    "unknown": 0
}
```
