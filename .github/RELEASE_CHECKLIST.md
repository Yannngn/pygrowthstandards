## Release checklist — automatic version bump & publish (GitHub Actions)

Use this checklist to ensure a smooth automatic release flow driven by semantic-release and the existing GitHub Actions workflows.

- [ ] Ensure `.releaserc.json` is present and configured (this repo already has one).
- [ ] Follow conventional commit messages (angular preset): `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, etc.
- [✅] Confirm `.github/workflows/semantic-release.yml` exists and is enabled (runs on pushes to `dev` and `main`).
- [✅] Confirm `.github/workflows/publish.yml` exists (publishes when tags starting with `v` are pushed).
- [✅] Verify `pyproject.toml` and `CHANGELOG.md` are tracked in git (they are updated by semantic-release).

Required repository secrets / permissions
- [✅] `GITHUB_TOKEN` — provided automatically to Actions (used by `semantic-release` to push tags/commit changelog)
- [✅] `PYPI_API_TOKEN` (or `TWINE_PASSWORD`) — set in repo secrets for the `pypa/gh-action-pypi-publish` step to publish to PyPI
- [✅] `TEST_PYPI_API_TOKEN` — set in repo secrets if you want TestPyPI publishing to use a separate token (optional)

How it works (high level)
- Merges to `dev`: `semantic-release` runs on push to `dev` and creates a *prerelease* (configured as `prerelease: true` and `channel: "next"`) based on conventional commits.
- Merges to `main`: `semantic-release` runs on push to `main` and creates a normal release (no prerelease tag).
- `semantic-release` will:
  - Analyze commits to determine the next version
  - Update `CHANGELOG.md` via the changelog plugin
  - Run the `exec.prepareCmd` to update `pyproject.toml` with `${nextRelease.version}`
  - Commit `CHANGELOG.md` and `pyproject.toml`, and create & push a `vX.Y.Z` tag
- The `publish.yml` workflow is triggered on tag pushes (`refs/tags/v*`). It builds the package, runs package checks, and publishes to TestPyPI and PyPI (using the uploaded artifacts).

Verification steps (local / quick checks)
- Run a dry-run of `semantic-release` locally to see what it would do:

```bash
npx semantic-release --dry-run
```

- Verify build & checks locally:

```bash
uvx build
uvx check dist/*
```

- If you prefer manual publishing, create and push a tag instead of relying on `semantic-release`:

```bash
git tag v1.2.3
git push origin v1.2.3
```

Notes & caveats
- Commits must follow conventional-commit rules for automatic bumps; otherwise `semantic-release` will not create a new release.
- `semantic-release` must have permission to push commits and tags back to the repository (the default `GITHUB_TOKEN` granted to Actions is usually sufficient).
- Ensure PyPI/TestPyPI tokens are set in repository secrets before expecting automatic publishing to succeed.

Want me to also update `PUBLISHING.md` with these condensed steps or scan recent commits to see whether a bump will be triggered automatically?
