import json
import logging
import logging.config
import os
import platform
import pwd
import sys
from typing import Any, cast

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


def init(program_name):
    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"handlers": ["console"], "level": "INFO"},
        "formatters": {
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "console": {
                "formatter": "json",
                "class": "logging.StreamHandler",
                "level": "INFO",
            }
        },
        "loggers": {
            "werkzeug": {"handlers": ["console"], "level": "WARN", "propagate": False},
            "app.api": {"handlers": ["console"], "level": "INFO", "propagate": False},
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
