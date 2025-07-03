# Getting Started

## Initializing Project:
### Install and Activate UV:
1. Install uv using `pip install uv`
2. Install dependencies `uv sync`
3. Activate venv `source .venv/bin/activate`

### Start FastAPI Development Server:
`uv run fastapi dev main.py`

## Database:
### Update Database:
`alembic upgrade head`

### Apply Revision:
`alembic revision --autogenerate -m "{name of revision}"`

## Debugging and Testing:
### VSCode Debugging:
Navigate to `main.py` activate VSCode Debugger
Mark Breakpoints as needed

### Integration Testing:
`pytest tests/integration/{name_of_test}.py`

### Ruff Checking:
`uv run ruff check`