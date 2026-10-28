# Contributing to SFFS

Thanks for your interest. SFFS is a course project split across three student modules plus an integration layer.

## Branching
- Never commit directly to `master`. Create a feature branch: `git checkout -b feat/short-description`.
- Open a pull request against `master`.

## Commit style
Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.

## Setup
```bash
python -m pip install -r main-code/requirements.txt
python -m pip install pytest ruff pre-commit
pre-commit install
```

## Running tests
```bash
pytest tests -q
```
All tests must pass before opening a PR.

## Module ownership
- `code1/` — Student 1 (crypto)
- `code2/` — Student 2 (security)
- `code3/` — Student 3 (UI/cloud)
- `main-code/` — integration

## Security
- Never commit `sffs_data/`, `security/`, `.env*`, `.pem`, or `.key` files.
- Never hardcode secrets; use `code1/f06_secure_key_storage.py`.
