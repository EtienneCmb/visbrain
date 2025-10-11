"""Generate static PNG assets for the documentation example gallery."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger("visbrain.generate_examples")


def _iter_example_scripts(root: Path) -> Iterable[Path]:
    for script in sorted(root.rglob("*.py")):
        if script.name.startswith("_"):
            continue
        yield script


def _resolve_image_name(script: Path) -> str | None:
    try:
        text = script.read_text(encoding="utf-8")
    except OSError as exc:
        LOGGER.warning("Unable to read %s: %s", script, exc)
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".. image::"):
            continue
        fragment = stripped.split(".. image::", 1)[1].strip()
        if not fragment:
            continue
        return Path(fragment).name
    return None


def _build_command(
    python_executable: str, script: Path, *, save_path: Path | None
) -> list[str]:
    command = [python_executable, str(script), "--no-show"]
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        command.extend(["--save", str(save_path)])
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "examples",
        help="Directory containing the example scripts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=(Path(__file__).resolve().parents[1] / "docs" / "_static" / "examples"),
        help="Directory where PNG renders should be stored.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter used to execute example scripts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands without executing them.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    examples_dir = args.examples_dir.resolve()
    output_dir = args.output_dir.resolve()
    python_exe = str(Path(args.python).resolve())

    if not examples_dir.exists():
        LOGGER.error("Examples directory %s does not exist", examples_dir)
        return 1

    LOGGER.info("Generating gallery assets from %s", examples_dir)
    if args.dry_run:
        LOGGER.info("Dry run enabled; no commands will be executed")

    failures: list[Path] = []

    for script in _iter_example_scripts(examples_dir):
        image_name = _resolve_image_name(script)
        if image_name is None:
            LOGGER.info(
                "Running %s without PNG export",
                script.relative_to(examples_dir),
            )
        save_path = output_dir / image_name if image_name else None
        command = _build_command(python_exe, script, save_path=save_path)
        if args.dry_run:
            LOGGER.info("Command: %s", " ".join(command))
            continue
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            LOGGER.error("Example %s failed with exit code %s", script, exc.returncode)
            failures.append(script)
            continue
        if save_path is not None:
            try:
                display = save_path.resolve().relative_to(output_dir)
            except ValueError:
                display = save_path
            LOGGER.info("Saved %s", display)

    if failures:
        LOGGER.error(
            "%d example(s) failed: %s",
            len(failures),
            ", ".join(map(str, failures)),
        )
        return 1

    LOGGER.info("Gallery assets stored in %s", output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
