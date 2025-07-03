# Instructions

### Install and Activate UV:
1. Install uv using `pip install uv`
2. Install dependencies `uv sync`
3. Activate venv `source .venv/bin/activate`

### Start FastAPI Development Server:
`uv run fastapi dev main.py`

### Ruff Checking:
`uv run ruff check`

### VSCode Debugging:
Navigate to `main.py` activate VSCode Debugger
Mark Breakpoints as needed

### Integration Testing:
`pytest tests/integration/{name_of_test}.py