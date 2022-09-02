import json
import logging
import logging.config
import os
import platform
import pwd
import sys
from datetime import datetime
from typing import Any, cast

from . import decodelog

# Attributes of LogRecord to exclude from the JSON formatted lines. An exclusion list approach is
# used so that all "extra" attributes can be included in a line.
EXCLUDE_ATTRIBUTES = {
    "args",
    "exc_info",
    "filename",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "msg",
    "pathname",
    "processName",
    "relativeCreated",
}


class JsonFormatter(logging.Formatter):  # noqa: B1
    """A logging formatter which formats each line as JSON."""

    def format(self, record):
        super(JsonFormatter, self).format(record)

        output = {
            key: value
            for key, value in record.__dict__.items()
            if key not in EXCLUDE_ATTRIBUTES and value is not None
        }

        return json.dumps(output, separators=(",", ":"))


class HumanReadableFormatter(logging.Formatter):
    """A logging formatter which formats each line
    as color-code human readable text
    """

    def format(self, record):
        super(HumanReadableFormatter, self).format(record)

        return decodelog.format_line(
            datetime.utcfromtimestamp(record.created),
            record.name,
            record.funcName,
            record.levelname,
            record.message,
            record.__dict__,
        )


def init(program_name):
    # Determine which log formatter to use
    # based on the environment variable specified
    # Defaults to JSON
    log_format = os.getenv("LOG_FORMAT", "json")

    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"handlers": ["console"], "level": "INFO"},
        "formatters": {
            "json": {"()": JsonFormatter},
            "human-readable": {"()": HumanReadableFormatter},
        },
        "handlers": {
            "console": {
                # Note the formatter specified here points
                # to the formatter specified above which
                # in turn points to the format classes
                "formatter": log_format,
                "class": "logging.StreamHandler",
                "level": "INFO",
            }
        },
        "loggers": {
            "alembic": {"handlers": ["console"], "level": "INFO", "propagate": False},
            "werkzeug": {"handlers": ["console"], "level": "WARN", "propagate": False},
            "api": {"handlers": ["console"], "level": "INFO", "propagate": False},
            # Log DB pool connection invalidations and recycle events. At DEBUG
            # level includes all connection checkin/checkouts to the pool.
            #
            # https://docs.sqlalchemy.org/en/13/core/engines.html#configuring-logging
            "sqlalchemy.pool": {"handlers": ["console"], "level": "INFO", "propagate": False},
            # Log PostgreSQL NOTICE messages
            # https://docs.sqlalchemy.org/en/13/dialects/postgresql.html#notice-logging
            "sqlalchemy.dialects.postgresql": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    logger.info(
        "start %s: %s %s %s, hostname %s, pid %i, user %i(%s)",
        program_name,
        platform.python_implementation(),
        platform.python_version(),
        platform.system(),
        platform.node(),
        os.getpid(),
        os.getuid(),
        pwd.getpwuid(os.getuid()).pw_name,
        extra={
            "hostname": platform.node(),
            "cpu_count": os.cpu_count(),
            # If mypy is run on a mac, it will throw a module has no attribute error, even though
            # we never actually access it with the conditional.
            #
            # However, we can't just silence this error, because on linux (e.g. CI/CD) that will
            # throw an unused “type: ignore” comment error. Casting to Any instead ensures this
            # passes regardless of where mypy is being run
            "cpu_usable": (
                len(cast(Any, os).sched_getaffinity(0))
                if "sched_getaffinity" in dir(os)
                else "unknown"
            ),
        },
    )
    logger.info("invoked as: %s", " ".join(original_argv))


def get_logger(name):
    """Return a logger with the specified name."""
    return logging.getLogger(name)


logger = get_logger(__name__)
original_argv = tuple(sys.argv)
