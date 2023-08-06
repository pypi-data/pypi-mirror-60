<p align="center">
<img src="https://pdfire.io/img/logo.svg" width="100" alt="PDFire.io logo">
</p>

# PDFire Python

![GitHub](https://img.shields.io/github/license/modernice/pdfire-python?style=flat-square)

This package provides a client for the [PDFire.io](https://pdfire.io) API. Read the [Documentation](https://docs.pdfire.io) for a list of available options.

## Installation

```sh
pip install pdfire
```

## Basic usage

```python
from pdfire import Client, ConversionParams

client = Client('YOUR-API-KEY')

pdf = client.convert(ConversionParams(
  url = 'https://google.com',
  margin = 0,
  format = 'A4',
))

pdf.save_to('/path/on/disk.pdf')
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
