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

```bash
uvicorn deciphon_api:app --reload
```

## Settings

Copy file `.env.example` to `.env` and edit it accordingly.
The rest of the configuration can be tuned by `uvicorn` options.
