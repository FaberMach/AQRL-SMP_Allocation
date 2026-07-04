# Contributing to AQRL

AQRL is designed as an institutional-grade research platform. Contributions must preserve architectural coherence, reproducibility, and scientific rigor.

## Workflow

1. Open or select a task from `TASKS.yaml`.
2. Read `PROJECT_BIBLE.md`, `AQRL_SPEC.yaml`, and relevant ADRs.
3. Implement the smallest possible coherent change.
4. Add tests.
5. Run quality checks.
6. Update documentation.
7. Submit a pull request.

## Quality Gates

Before a PR is considered ready:

```bash
ruff check .
black --check .
mypy aqrl
pytest
```

## Coding Standards

- Python 3.12+
- Type hints for all public functions
- Google-style docstrings
- No duplicated logic
- No hidden global state
- Prefer small modules with explicit contracts
- Financial algorithms must include references, assumptions, and limitations
