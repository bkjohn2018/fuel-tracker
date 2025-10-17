# Contributing

We use **Conventional Commits** and maintain a **Keep a Changelog**.
- feat:, fix:, docs:, chore:, ci:, refactor:, test:, perf:, build:

## Local Dev
- Python version: match repo config / CI
- Install: `poetry install` or `pip install -e .`
- Lint: `make lint`
- Test: `make test`

## Docs-Only Changes
- Prefer `docs:` scope
- Update `CHANGELOG.md` under Unreleased or next tag
- For compliance content, avoid paraphrasing beyond approved text blocks

## Releasing
1. Update `CHANGELOG.md`
2. Open PR with `docs(release): prepare vX.Y.Z`
3. After merge, tag `vX.Y.Z` and publish GitHub Release using `.github/RELEASE_TEMPLATE.md`
