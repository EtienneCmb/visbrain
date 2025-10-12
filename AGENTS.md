# Agent Instructions

## Scope
These guidelines apply to the entire repository unless a subdirectory adds its own `AGENTS.md` with more specific directions.

## Environment Setup
- Use Python 3.9+.
- Install tooling with `python -m pip install -r requirements/dev.txt` before running tests or linters.
- Ensure system OpenGL libraries are available: `apt-get update` followed by `apt-get install -y libgl1 libglu1-mesa libgl1-mesa-dri mesa-utils libxcb-xinerama0`. These packages avoid the `libGL.so.1` import failures during PySide6/VisPy initialization.
- When using the provided Makefile targets, the repository expects `tox` and `twine` to be invokable via `python -m ...` so there is no need to modify your shell `PATH`.

## Required Checks
When you modify any files:
1. Run `make flake` for linting (this internally calls `python -m tox -e lint`).
2. Run `pytest` (or `make test`) for automated tests. If you need to exercise the tox environment directly, prefer `python -m tox -e tests` so that the pinned interpreter is used even when console scripts are not on the `PATH`.
3. Run additional commands mentioned in the relevant documentation if your changes affect packaging (e.g., `python -m build`).
Document all executed commands and their outcomes in the final response.

## Coding Conventions
- Prefer modern Python features compatible with the supported versions (3.9+).
- Avoid introducing new runtime downloads; package assets via the build system instead.
- Keep Makefile targets compatible with POSIX sh.

## Documentation
- Update the modernization roadmap under `docs/modernization/` when you make significant plan adjustments.
- Keep README instructions aligned with the current tooling workflow.

## Testing Notes
- GUI smoke tests may require a display; prefer headless-friendly flags such as `--visbrain-show=False` when adding or updating examples.

## Pull Requests
- Provide concise summaries highlighting the impact and include the commands run for validation.
- Ensure the working tree is clean before completion.
