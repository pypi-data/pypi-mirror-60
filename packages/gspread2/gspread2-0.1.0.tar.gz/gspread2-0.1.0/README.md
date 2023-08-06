![Stage](https://img.shields.io/badge/Stage-BETA-yellow)
[![PyPI](https://img.shields.io/pypi/v/gspread2)](https://pypi.org/project/gspread2)
[![gspread](https://img.shields.io/badge/gspread-3.1.0-blue)](https://github.com/burnash/gspread)
[![Documentation Status](https://readthedocs.org/projects/gspread2/badge/?version=latest)](https://gspread2.readthedocs.io/en/latest/?badge=latest)


# Gspread2

A wrapper around [gspread](https://github.com/burnash/gspread) for easier usage.
Intended to provide features and syntax similar to [OpenPyXL](https://bitbucket.org/openpyxl/openpyxl).

> DISCLAIMER: This library is still under development!

## Features

- Cell Formatting such as Fonts, Colors and Borders
- OpenPyXL functions such as `iter_rows()` and `iter_cols()`
- Values are automatically applied to the sheet when updated

## Roadmap/TODO

- Documentation (WIP)
- Formulas
- Filters and Pivot Tables

## Installation

### Requirements:
- Python3.6+

### Install via Pip
```
$ pip install gspread2
```

## Basic Usage

### Getting Started

#### Create API credentials

Before using this library, you must log into Google Developers page and set up a Service Account,
allowing read/write access to your Google Sheets.

1. Head to [Google Developers Console](https://console.developers.google.com/project) 
and create a new project (or select the one you have.)

2. Navigate to "API & Services", "Credentials".

3. Click on "CREATE CREDENTIALS", "Service account" and follow through the prompts.
On the last page, create a JSON key and save it locally. You will need to import this into the library to authenticate
to the API.

4. Once you hit "Done", you will see the email address under "Service Accounts", make note of that email.

5. On your Google Sheet, hit "Share" and add the email above.

6. You should now have the credentials and permissions to view and edit your Google Sheet.

#### Load Workbook

To access a Workbook, you'll need the Google Sheet URL and the credentials file as shown above.
The following code example will return a Workbook object:

```python
import gspread2

URL = 'https://docs.google.com/spreadsheets/d/spreadsheetID'
CREDENTIALS = 'path/to/json.file'

workbook = gspread2.load_workbook(URL, CREDENTIALS)
```

You can also import the Workbook class and initialise it with the same parameters:

```python
from gspread2.models import Workbook

URL = 'https://docs.google.com/spreadsheets/d/spreadsheetID'
CREDENTIALS = 'path/to/json.file'

workbook = Workbook(URL, CREDENTIALS)
```

#### Load Worksheet

Once you have a Workbook loaded, you can access worksheets in a number of ways:

```python
workbook = gspread2.load_workbook(URL, CREDENTIALS)
worksheet = workbook['Sheet 1']
```

OR

```python
workbook = gspread2.load_workbook(URL, CREDENTIALS)
worksheet = workbook.get_sheet_by_name('Sheet 1')
```

To get the first sheet (usually the active one):

```python
workbook = gspread2.load_workbook(URL, CREDENTIALS)
worksheet = workbook.active
```
