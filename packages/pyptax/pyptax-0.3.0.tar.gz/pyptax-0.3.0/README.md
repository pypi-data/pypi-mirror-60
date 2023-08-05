<h1 align="center">
  PyPtax
</h1>

<h4 align="center">PyPtax is a Python library to retrieve information on <i><a href="#what-is-ptax">Ptax rates</a></i></h4>

<p align="center">
  <a href="https://pypi.python.org/pypi/pyptax">
    <img src="https://img.shields.io/pypi/v/pyptax.svg?style=flat-square" alt="Latest Version"/>
  </a>
  <a href="https://travis-ci.org/brunobcardoso/pyptax">
    <img src="https://img.shields.io/travis/brunobcardoso/pyptax/master.svg?style=flat-square" alt="Build Status"/>
  </a>
  <a href="https://codecov.io/gh/brunobcardoso/pyptax">
    <img src="https://codecov.io/gh/brunobcardoso/pyptax/branch/master/graph/badge.svg" alt="Coverage"/>
  </a>
  <a href="https://pypi.python.org/pypi/pyptax/">
    <img src="https://img.shields.io/pypi/pyversions/pyptax.svg?style=flat-square" alt="Supported Versions"/>
  </a>
  <a href='https://pyptax.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://img.shields.io/readthedocs/pyptax/latest?style=flat-square' alt='Documentation Status'/>
  </a>
  <a href='https://github.com/psf/black'>
    <img src='https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square' alt='Code Style'/>
  </a>
</p>

<p align="center">
  <a href="#installation">Installation</a> |
  <a href="#usage">Usage</a> |
  <a href="#documentation">Documentation</a> |
  <a href="#contributing">Contributing</a>
</p>

## What is Ptax?

[Ptax exchange rate](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE042_A_taxa_de_cambio_de_referencia_Ptax.pdf)
is the reference exchange rate for U.S. Dollar, expressed as the amount of Brazilian Reais per one U.S. Dollar,
published by the [Central Bank of Brazil](https://www.bcb.gov.br/en).

## Installation
```bash
$ pip install pyptax
```

## Usage

### Get closing rates on a certain date

```python
>>> from pyptax import ptax
>>> close_report = ptax.close('2020-01-20')
>>> close_report.as_dict
{'datetime': '2020-01-20 13:09:02.871', 'bid': '4.1823', 'ask': '4.1829'}
>>> close_report.datetime
'2020-01-20 13:09:02.871'
>>> close_report.bid
'4.1823'
>>> close_report.ask
'4.1829'
```

## Documentation

The full documentation is available on https://pyptax.readthedocs.io/.

## Contributing

Please see the [contributing page](https://github.com/brunobcardoso/pyptax/blob/master/CONTRIBUTING.rst)
for guidance on setting up a development environment and how to contribute.
