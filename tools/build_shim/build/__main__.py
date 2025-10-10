from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Iterable, List, Sequence


_SHIM_ROOT = Path(__file__).resolve().parent.parent


@contextmanager
def _without_shim() -> Iterable[None]:
    saved_path = list(sys.path)
    saved_module = sys.modules.pop("build", None)
    try:
        sys.path = [p for p in sys.path if Path(p).resolve() != _SHIM_ROOT]
        yield
    finally:
        sys.path = saved_path
        if saved_module is not None:
            sys.modules["build"] = saved_module


def _load_real_build_main() -> ModuleType:
    """Load the upstream ``build.__main__`` module."""
    with _without_shim():
        return importlib.import_module("build.__main__")


def _twine_check(artifacts: Iterable[Path]) -> int:
    args: List[str] = [str(path) for path in artifacts]
    if not args:
        return 1
    completed = subprocess.run(
        [sys.executable, "-m", "twine", "check", *args],
        check=False,
    )
    return completed.returncode


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    real_main = _load_real_build_main().main  # type: ignore[attr-defined]
    if "--check" in args:
        args = [arg for arg in args if arg != "--check"]
        outdir = Path(tempfile.mkdtemp(prefix="visbrain-build-check-"))
        try:
            status = real_main([*args, "--outdir", str(outdir)])
            if status:
                return status
            return _twine_check(sorted(outdir.iterdir()))
        finally:
            shutil.rmtree(outdir, ignore_errors=True)
    return real_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
