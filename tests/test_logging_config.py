
import logging

from dataqualityprofiler.logging_config import configure_logging


def test_configure_logging_sets_root_level():
    configure_logging(logging.WARNING)

    assert logging.getLogger().level == logging.WARNING