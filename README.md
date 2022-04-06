# deciphon-api

## Install

```bash
pip install deciphon-api
```

## Production

```bash
uvicorn deciphon_api:app --host 127.0.0.1 --port 8000
```

## Development

Make sure you have [Poetry](https://python-poetry.org/docs/).

Enter

```bash
poetry install
poetry shell
```

to setup and activate a Python environment associated with the project.
Then enter

```bash
uvicorn deciphon_api:app --reload
```

to start the API.

Tests can be performed by entering

```bash
pytest
```

while the corresponding Python environment created by Poetry is active.

## Settings

Copy file `.env.example` to `.env` and edit it accordingly.
The rest of the configuration can be tuned by `uvicorn` options.
