"""Generate Sphinx-Gallery thumbnail placeholders from bundled screenshots."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from sphinx_gallery.gen_rst import scale_image

try:  # pragma: no cover - compatibility shim for older Sphinx-Gallery releases
    from sphinx_gallery import sphinx_compatibility
except ImportError:  # sphinx-gallery 0.15 removed the helper module
    sphinx_compatibility = None  # type: ignore[assignment]


def _configure_logger() -> logging.Logger:
    if sphinx_compatibility is not None:
        logger = sphinx_compatibility.getLogger("sphinx")
    else:
        logger = logging.getLogger("sphinx-gallery")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def _parse_arguments() -> argparse.Namespace:
    docs_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=docs_dir.parent / "examples",
        help="Root directory containing the example scripts.",
    )
    parser.add_argument(
        "--static-dir",
        type=Path,
        default=docs_dir / "_static" / "examples",
        help="Directory holding the pre-rendered example screenshots.",
    )
    parser.add_argument(
        "--thumb-root",
        type=Path,
        default=docs_dir / "_build" / "html" / "_images",
        help="Destination directory for the generated thumbnail PNGs.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=400,
        help="Width of the generated thumbnails in pixels.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=280,
        help="Height of the generated thumbnails in pixels.",
    )
    return parser.parse_args()


def _discover_static_image(script: Path) -> Path | None:
    try:
        text = script.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".. image::"):
            continue
        fragment = stripped.split(".. image::", 1)[1].strip()
        if fragment:
            return Path(fragment)
    return None


def _thumbnail_directory(thumb_root: Path, script: Path, examples_dir: Path) -> Path:
    relative = script.relative_to(examples_dir)
    base = relative.with_suffix("")
    image_subpath = Path("sphx_glr_" + base.as_posix())
    return thumb_root / image_subpath.parent / "thumb"


def main() -> int:
    args = _parse_arguments()
    logger = _configure_logger()

    examples_dir = args.examples_dir.resolve()
    static_dir = args.static_dir.resolve()
    thumb_root = args.thumb_root.resolve()
    thumb_root.mkdir(parents=True, exist_ok=True)

    logger.info("generating thumbnails using example images from %s", static_dir)

    for script in sorted(examples_dir.rglob("*.py")):
        if script.name.startswith("_"):
            continue
        image_fragment = _discover_static_image(script)
        if image_fragment is None:
            logger.warning("        No image defined in %s", script)
            continue
        source_image = static_dir / image_fragment.name
        if not source_image.exists():
            logger.warning("        Missing screenshot for %s", script)
            continue
        thumb_dir = _thumbnail_directory(thumb_root, script, examples_dir)
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_name = f"sphx_glr_{script.stem}_thumb.png"
        destination = thumb_dir / thumb_name
        scale_image(str(source_image), str(destination), args.width, args.height)
        logger.info("        Thumbnail created %s", destination.relative_to(thumb_root))

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
