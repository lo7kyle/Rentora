# Rentora

Renting with Aura.

## Module 1: Pydantic & Data Contracts

This module establishes the validated data boundary for rental listings:

- `RawListingInput` represents unprocessed listing text and its source.
- `ParsedRentalListing` represents structured listing facts.
- Enums constrain laundry and parking categories.
- Field metadata documents the contract; validators normalize state codes,
  monthly prices, and bathroom values.

### Project structure

```text
app/
  __init__.py
  schemas.py
tests/
  __init__.py
  test_schemas.py
requirements.txt
requirements-dev.txt
```

### Setup

Use Python 3.11 or newer. From the repository root, create and activate a
virtual environment, then install the development dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run the schema tests with:

```powershell
python -m pytest
```

The next step is to use these contracts when building the local parser in
Module 2.
