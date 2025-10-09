"""Command line entry points for :mod:`visbrain`."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .config import get_config


def _guidance_from_diagnostics(payload: dict[str, Any]) -> str:
    """Return actionable guidance derived from the diagnostics payload."""

    available = payload.get("available", False)
    context = payload.get("context_available", False)
    shader_compiled = payload.get("shader_compiled")
    shader_error = payload.get("shader_error")
    fallback_reason = payload.get("fallback_reason")

    if not available:
        error = payload.get("error") or "backend unavailable"
        return (
            "VisPy backend is unavailable (%s). Ensure the 'vispy' package is "
            "installed and GPU drivers or headless libraries (EGL/OSMesa) are "
            "present."
        ) % error
    if not context:
        return (
            "OpenGL context could not be created. Configure a display server or "
            "install EGL/OSMesa for headless rendering."
        )
    if shader_compiled is False:
        return (
            "Shader compilation failed (%s). Update GPU drivers or verify that "
            "the OpenGL implementation supports GLSL." % (shader_error or "unknown")
        )
    if fallback_reason and "Configured headless" in fallback_reason:
        return (
            f"Headless rendering active ({fallback_reason}). Ensure texture limits "
            "meet workload requirements."
        )
    return "OpenGL diagnostics look healthy."


def _format_payload(payload: dict[str, Any]) -> list[str]:
    """Return human readable lines for the diagnostics payload."""

    lines = []
    for key in sorted(payload):
        value = payload[key]
        if key == "headless_attempts" and isinstance(value, list):
            formatted: list[str] = []
            for attempt in value:
                backend = attempt.get("backend") or "n/a"
                status = "ok" if attempt.get("success") else "fail"
                formatted.append(f"{backend}={status}")
            lines.append(f"{key}: {', '.join(formatted)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def main(argv: list[str] | None = None) -> int:
    """Entry point executed via ``python -m visbrain``."""

    parser = argparse.ArgumentParser(prog="visbrain", add_help=True)
    subparsers = parser.add_subparsers(dest="command")

    info_parser = subparsers.add_parser(
        "info", help="Display OpenGL/VisPy diagnostics"
    )
    info_parser.add_argument(
        "--json", action="store_true", help="Emit diagnostics in JSON format"
    )

    args = parser.parse_args(argv)

    if args.command == "info":
        config = get_config()
        diagnostics = config.refresh_vispy_diagnostics(log=True)
        payload = config.vispy_diagnostics_payload or diagnostics.payload()
        if args.json:
            json.dump(payload, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            print("Visbrain OpenGL diagnostics")
            for line in _format_payload(payload):
                print(f"  - {line}")
            print()
            print("Guidance:")
            guidance = _guidance_from_diagnostics(payload)
            print(f"  {guidance}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
