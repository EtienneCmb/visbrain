"""Asynchronous helpers for loading sleep datasets."""
from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Callable

from visbrain.io.background import run_in_loader_thread, shutdown_loader_threads


class AsyncSleepLoader:
    """Load :class:`~visbrain.io.read_sleep.ReadSleepData` objects in a thread."""

    def shutdown(self) -> None:
        """Shut down the shared loader executor."""

        shutdown_loader_threads(wait=False)

    def submit(
        self,
        function: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Future:
        """Submit *function* to the shared loader executor."""

        return run_in_loader_thread(function, *args, **kwargs)
