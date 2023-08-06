# Isogeo Scan - Metadatas Processor

[![Build Status](https://dev.azure.com/isogeo/Scan/_apis/build/status/isogeo.scan-metadata-processor?branchName=master)](https://dev.azure.com/isogeo/Scan/_build/latest?definitionId=54&branchName=master)

[![Documentation: sphinx](https://img.shields.io/badge/doc-sphinx--auto--generated-blue)](http://help.isogeo.com/scan/isogeo-scan-metadata-processor/index.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Run Isogeo Scan without the web application interface, RabbitMQ and MongoDB.

## Requirements

- Python 3.7

## Development

### Quickstart

```powershell
# create virtual env
py -3.7 -m venv .venv
# activate it
.\.venv\Scripts\activate
# update basic tooling
python -m pip install -U pip setuptools wheel
# install requirements
python -m pip install -U -r ./requirements.txt
# install package for development
python -m pip install --editable .
```

### Try it

1. Rename the `.env.example` into `.env` and fill the settings
2. Launch the [CLI](https://fr.wikipedia.org/wiki/Interface_en_ligne_de_commande)

For example, get the help:

```powershell
scan-metadata-processor --help
```

Example with Isogeo SharePoint:

```powershell
# for all default formats
scan-metadata-processor --settings ./.env --directory "C:\Users\JulienMOURA\ISOGEO\SIG - Documents\TESTS\SCAN_FME"
# with other environment file and only for Esri shapefiles
scan-metadata-processor --settings ./dev.env --directory "C:\Users\JulienMOURA\ISOGEO\SIG - Documents\TESTS\SCAN_FME" --formats shp
```

There is also a clean task to automatically remove outdated logs and output files:

```powershell
scan-metadata-processor --settings ./dev.env --directory "C:\Users\JulienMOURA\ISOGEO\SIG - Documents\TESTS\SCAN_FME" clean
```

## Usage of the executable

Just replace `scan-metadata-processor` by the executable filename:

```powershell
.\Isogeo_ScanMetadataProcessor.exe --settings ./.env --directory "C:\Users\JulienMOURA\ISOGEO\SIG - Documents\TESTS\SCAN_FME" --formats shp
```

----

## Deployment

The deployment is not automated but it's simple: download the latest Azure Pipeline artifact as zip file and complete environment file with releveant parameters.

### Obfuscating the Azure Storage key

Because the CLI needs to include the Azure Storage account key with write rights, the key is encoded during the build into executable. See [the sample script detailing this behavior](https://github.com/isogeo/scan-metadata-processor/blob/master/tests/dev/dev_encode_key.py).
