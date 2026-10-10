#
# Copyright (c) 2026 Boxel Studio.
#
# :Module: pipeline_configuration_init
# :Description: Core hook run every time a PipelineConfiguration
#  instance is created - before any engine starts and before the
#  bootstrap caches bundles. Used here to silence known, harmless
#  tk-core warnings.
#
# :Author: Fidel Moreno Miranda <fidel.moreno@boxelstudio.com>
#

# Standard modules
import logging

# Third-party modules
from tank import Hook  # type: ignore

# Logger name -> start of the one WARNING message dropped from it.
# Nothing else those loggers write is affected.
_KNOWN_WARNINGS = {
    # SG Desktop's Python 3.13 ships a PySide2 without shiboken2, so
    # tk-core can't load a Qt5 binding and falls back to PySide6 -
    # everything works, but the warning is logged on every engine
    # start, and tk-framework-desktopserver relays it to ShotGrid Web
    # as a "Command Output" popup after every action menu command.
    "sgtk.core.util.qt_importer": (
        "Unable to import a Qt binding for the Qt5 interface"),
    # Boxel's own "app_store" bundles really come from
    # CustomNonProjectEntity02 (see bootstrap.py); after downloading
    # one, tk-core still tries to log a download stat on Autodesk's
    # official App Store, which doesn't know the bundle.
    "sgtk.core.descriptor.io_descriptor.appstore": (
        "Could not write app store download receipt"),
}


class _KnownWarningFilter(logging.Filter):
    """Drop one known, harmless WARNING message, and only that one."""

    def __init__(self, message_start: str):
        """Build the filter.

        Args:
            message_start: Start of the warning message to drop.
        """
        super().__init__()
        self._message_start = message_start

    def filter(self, record: logging.LogRecord) -> bool:
        """Decide whether a log record is kept.

        Args:
            record: The log record being emitted.

        Returns:
            False for the known warning, True otherwise.
        """
        return not (
            record.levelno == logging.WARNING
            and record.getMessage().startswith(self._message_start))


class PipelineConfigurationInit(Hook):
    """Core hook run when a PipelineConfiguration is initialized."""

    def execute(self, **kwargs) -> None:
        """Install the known-warning filters, once per process.

        Args:
            **kwargs: Unused, part of the hook signature.
        """
        for logger_name, message_start in _KNOWN_WARNINGS.items():
            logger = logging.getLogger(logger_name)
            if not any(isinstance(f, _KnownWarningFilter)
                       for f in logger.filters):
                logger.addFilter(_KnownWarningFilter(message_start))
