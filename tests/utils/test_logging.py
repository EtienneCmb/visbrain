"""Tests for the Visbrain logging helpers."""

from __future__ import annotations

from visbrain.utils import logging as vb_logging


def test_pattern_match_with_format_args(caplog):
    """Ensure pattern highlighting works with %-style arguments."""

    handler = vb_logging._lh  # access module handler to restore after test
    old_pattern = handler._str_pattern
    try:
        vb_logging.set_log_level(verbose="INFO", match="dataset")
        with caplog.at_level("INFO", logger=vb_logging.logger.name):
            vb_logging.logger.info("Loading dataset from %s", "path.edf")
    finally:
        handler._str_pattern = old_pattern

    assert any("*dataset*" in record.getMessage() for record in caplog.records)
    assert any("path.edf" in record.getMessage() for record in caplog.records)
