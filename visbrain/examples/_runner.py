"""Utility helpers for executing example scripts in a consistent manner."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from visbrain import config

logger = logging.getLogger("visbrain.examples")


def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a Visbrain example in headless-friendly mode."
        )
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        help="Persist a screenshot or exported figure to PATH.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Skip displaying the interactive window.",
    )
    return parser.parse_args(argv)


def _iter_targets(result: Any) -> Iterator[Any]:
    if result is None:
        return
    if isinstance(result, dict):
        for item in result.values():
            yield from _iter_targets(item)
        return
    if isinstance(result, (list, tuple, set)):
        for item in result:
            yield from _iter_targets(item)
        return
    yield result


def _is_matplotlib_figure(obj: Any) -> bool:
    try:
        from matplotlib.figure import Figure
    except Exception:  # pragma: no cover - matplotlib is optional
        return False
    return isinstance(obj, Figure)


def _callable_attribute(obj: Any, name: str) -> Any:
    attr = getattr(obj, name, None)
    return attr if callable(attr) else None


def _save_target(target: Any, path: Path) -> bool | None:
    if target is None:
        return None
    custom = _callable_attribute(target, "_example_save")
    if custom is not None:
        custom(str(path))
        return True
    screenshot = _callable_attribute(target, "screenshot")
    if screenshot is not None:
        screenshot(str(path))
        return True
    saver = _callable_attribute(target, "save")
    if saver is not None:
        saver(str(path))
        return True
    if _is_matplotlib_figure(target):
        savefig = _callable_attribute(target, "savefig")
        if savefig is not None:
            savefig(str(path))
            return True
    try:
        from visbrain._pyqt_module import _PyQtModule
        from visbrain.io import write_fig_qt
    except Exception:  # pragma: no cover - optional in minimal installs
        _PyQtModule = None  # type: ignore[assignment]
        write_fig_qt = None  # type: ignore[assignment]
    if _PyQtModule is not None and isinstance(target, _PyQtModule):
        if write_fig_qt is not None:
            write_fig_qt(target, str(path))
            return True
    return None


def _show_target(target: Any) -> bool | None:
    if target is None:
        return None
    custom = _callable_attribute(target, "_example_show")
    if custom is not None:
        custom()
        return True
    method = _callable_attribute(target, "show")
    if method is not None:
        method()
        return True
    if _is_matplotlib_figure(target):
        try:
            import matplotlib.pyplot as plt
        except Exception:  # pragma: no cover - matplotlib optional
            return None
        plt.show()
        return True
    return None


def _perform_action(
    targets: Iterable[Any],
    action,
    *,
    description: str,
) -> bool:
    handled = False
    supported = False
    for target in targets:
        try:
            success = action(target)
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.warning(
                "Failed to %s for %r due to %s", description, target, exc, exc_info=True
            )
            return False
        if success:
            handled = True
            supported = True
        elif success is False:
            supported = True
    if handled:
        return True
    if not supported:
        logger.debug("No targets support the '%s' action", description)
        return True
    return False


def run_example(
    factory,
    *,
    argv: Sequence[str] | None = None,
    description: str | None = None,
) -> int:
    """Execute *factory* under the example runner with CLI controls."""

    args = _parse_arguments(argv)
    if description:
        logger.info("Running example: %s", description)
    cfg = config.configure_headless(force=True)
    cfg.refresh_vispy_diagnostics(log=True)

    save_path = Path(args.save).expanduser() if args.save else None
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = factory()
    except Exception as exc:  # pragma: no cover - user example failure
        logger.exception("Example execution failed: %s", exc)
        return 1

    targets = list(_iter_targets(result))

    exit_code = 0

    if save_path is not None:
        if not _perform_action(
            targets,
            lambda obj: _save_target(obj, save_path),
            description="save output",
        ):
            logger.warning("Unable to produce output at %s", save_path)
            exit_code = 1

    if not args.no_show:
        if not _perform_action(
            targets,
            _show_target,
            description="display example",
        ):
            logger.warning("Rendering aborted; see warnings above for details")
            exit_code = 1

    return exit_code


__all__ = ["run_example"]

