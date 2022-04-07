# deciphon-api

## Install

```bash
pip install deciphon-api
```

## Production

```bash
uvicorn deciphon_api.main:app.api --host 127.0.0.1 --port 8000
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
uvicorn deciphon_api.main:app.api --reload
```

to start the API.

Tests can be performed by entering

```bash
pytest
```

while the corresponding Python environment created by Poetry is active.

## Settings

Copy the file [.env.example](.env.example) to your working directory and rename it to `.env`.
Edit it accordingly.
The rest of the configuration can be tuned by `uvicorn` options.
