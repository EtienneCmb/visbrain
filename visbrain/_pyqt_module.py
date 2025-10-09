"""All visbrain modules based on Qt should inherit from _PyQtModule."""
from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from typing import Any, List, Sequence, Tuple

from .qt import QtGui, QtWidgets, guard_qapp_lifecycle

from .utils import set_widget_size, set_log_level
from .config import PROFILER, get_config, qt_app, vispy_app
from pathlib import Path

from .io import cache_manager, path_to_visbrain_data
from .resources import load_icon
from .gui.theme import theme_manager

logger = logging.getLogger('visbrain')

guard_qapp_lifecycle()


class _PyQtModule(object):
    """Shared methods across PyQt based Visbrain modules.

    Parameters
    ----------
    verbose : logging.level | None
        Verbosity level.
    to_describe : string | None
        The parent node to describe. Only available if verbose level is on
        debug.
    icon : str | None
        Name of the icon to use.
    """

    def __init__(self, verbose=None, to_describe=None, icon=None,
                 show_settings=True):
        """Init."""
        # Log level and profiler creation (if verbose='debug')
        set_log_level(verbose)
        path_to_visbrain_data(create=True, allow_bundled=False)
        self._cache_owner = f"pyqt:{id(self)}"
        self._cache_session: Path | None = None
        self._create_tmp_folder()
        if logger.level == 10:
            import faulthandler
            faulthandler.enable()
            logger.debug("Faulthandler enabled")
        self._description_hooks: List[Tuple[str, Callable[[], str]]] = []
        self._register_description_hooks(to_describe)
        self._module_icon = icon
        self._show_settings = show_settings
        self._theme_manager = theme_manager
        self._theme_manager.ensure_application_theme()

    ###########################################################################
    #                               TMP FOLDER
    ###########################################################################

    def _path_to_tmp_folder(self):
        return str(self._ensure_tmp_session())

    def _create_tmp_folder(self):
        session_path = self._ensure_tmp_session()
        logger.debug("tmp folder created (%s)." % session_path)

    def _clean_tmp_folder(self):
        session = self._cache_session
        cache_manager.cleanup_owner(self._cache_owner)
        self._cache_session = None
        logger.debug("tmp folder cleaned (%s)." % session)

    def _ensure_tmp_session(self) -> Path:
        if self._cache_session is None or not self._cache_session.exists():
            self._cache_session = cache_manager.new_session(
                self._cache_owner,
                prefix='pyqt',
            )
        return self._cache_session

    ###########################################################################
    #                            SHOW // CLOSE
    ###########################################################################
    def _pyqt_title(self, title, msg, symbol='='):
        """Define a PyQt title."""
        assert isinstance(title, str) and isinstance(symbol, str)
        n_symbol = 60
        start_title = int((n_symbol / 2) - (len(title) / 2)) - 1
        upper_bar = symbol * n_symbol
        title_bar = ' ' * start_title + title
        title_template = "\n%s\n%s\n\n{msg}" % (upper_bar, title_bar)
        logger.profiler(title_template.format(msg=msg))

    def show(self):
        """Display the graphical user interface."""
        with qt_app() as app:
            if hasattr(self, 'q_widget') and app is not None:
                set_widget_size(app, self.q_widget, 23)
                self.q_widget.setVisible(self._show_settings)
            # Force the quick settings tab to be on the first tab :
            if hasattr(self, 'QuickSettings'):
                self.QuickSettings.setCurrentIndex(0)
            # Set icon (if possible) :
            if isinstance(self._module_icon, str):
                app_icon = load_icon(self._module_icon)
                if app_icon is not None:
                    self.setWindowIcon(app_icon)
                else:  # don't crash just for an icon...
                    logger.debug("No icon found (%s)" % self._module_icon)
            elif isinstance(self._module_icon, QtGui.QIcon):
                self.setWindowIcon(self._module_icon)
            elif self._module_icon is not None:
                logger.debug("Unsupported icon type: %r", self._module_icon)
            else:
                logger.debug("No icon passed as an input.")
            # Tree description if log level is on debug :
            if self._description_hooks:
                for label, callback in self._description_hooks:
                    try:
                        description = callback()
                    except Exception:
                        logger.exception(
                            "Failed to describe tree for %s", label
                        )
                        raise
                    else:
                        self._pyqt_title('Tree', description)
            # Show and maximized the window :
            if PROFILER and logger.level == 1:
                self._pyqt_title('Profiler', '')
                PROFILER.finish()
            # If PyQt GUI :
            cfg = get_config()
            if cfg.show_pyqt_app:
                self.showMaximized()
                with vispy_app(run=cfg.show_gui):
                    pass
        # Finally clean the tmp folder :
        self._clean_tmp_folder()

    def closeEvent(self, event):  # noqa
        """Executed method when the GUI closed."""
        cfg = get_config()
        app = cfg.get_qt_app(create=False)
        if app is not None:
            app.quit()
        logger.debug("App closed.")

    # ------------------------------------------------------------------
    # Theme helpers
    # ------------------------------------------------------------------
    def _apply_theme(self, widget: QtWidgets.QWidget | None = None) -> None:
        """Apply the active Visbrain theme to *widget* or the module window."""

        target = widget
        if target is None:
            target = getattr(self, "q_widget", None)
            if target is None and isinstance(self, QtWidgets.QWidget):
                target = self
        self._theme_manager.apply(widget=target)

    # ------------------------------------------------------------------
    # Description helpers
    # ------------------------------------------------------------------
    def _register_description_hooks(self, specs: Any) -> None:
        for label, callback in self._iter_description_specs(specs):
            self._description_hooks.append((label, callback))

    def add_description_hook(
        self, callback: Callable[[], str], *, label: str | None = None
    ) -> None:
        """Register an explicit *callback* returning a tree description."""

        hook_label = label or getattr(callback, "__name__", repr(callback))
        self._description_hooks.append((hook_label, callback))

    # -- internal utilities -------------------------------------------------
    def _iter_description_specs(
        self, specs: Any
    ) -> Iterable[Tuple[str, Callable[[], str]]]:
        if specs is None:
            return
        if isinstance(specs, (list, tuple, set)):
            for item in specs:
                yield from self._iter_description_specs(item)
            return
        if isinstance(specs, str):
            yield (specs, self._make_describe_tree_callback(specs))
            return
        describe = getattr(specs, "describe_tree", None)
        if callable(describe):
            label = getattr(specs, "__class__", type(specs)).__name__
            yield (label, describe)
            return
        if callable(specs):
            label = getattr(specs, "__name__", repr(specs))
            yield (label, specs)
            return
        raise TypeError(f"Unsupported description hook specification: {specs!r}")

    def _make_describe_tree_callback(
        self, dotted_path: str
    ) -> Callable[[], str]:
        parts: Sequence[str] = tuple(filter(None, dotted_path.split('.')))

        def _describe() -> str:
            target: Any = self
            for part in parts:
                try:
                    target = getattr(target, part)
                except AttributeError as exc:
                    raise AttributeError(
                        f"Attribute path {dotted_path!r} missing {part!r}"
                    ) from exc
            describe = getattr(target, "describe_tree", None)
            if not callable(describe):
                raise AttributeError(
                    f"Resolved object for {dotted_path!r} has no describe_tree"
                )
            return describe()

        return _describe
