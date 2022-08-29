import datetime
import logging
import logging.config
import os
import platform
import pwd
import sys
from typing import Any, cast

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"
NO_COLOUR = ""


def colour_for_level(level: str) -> str:
    if level in ("WARNING", "ERROR", "CRITICAL"):
        return RED
    return NO_COLOUR


EXCLUDE_EXTRA = {
    "args",
    "created",
    "entity.guid",
    "entity.name",
    "entity.type",
    "exc_info",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "span.id",
    "thread",
    "threadName",
    "trace.id",
    "traceId",
}


class DevelopFormatter(logging.Formatter):  # noqa: B1
    """A logging formatter which formats each line as text."""

    def format(self, record):
        super(DevelopFormatter, self).format(record)

        created_at = datetime.datetime.utcfromtimestamp(record.created)

        return "%s  %s%-36s%s %-28s %s%-8s %-80s %s%s%s" % (
            created_at.isoformat(),
            GREEN,
            record.name,
            RESET,
            record.funcName,
            colour_for_level(record.levelname),
            record.levelname,
            record.message,
            BLUE,
            " ".join(
                "%s=%s" % (key, value)
                for key, value in record.__dict__.items()
                if key not in EXCLUDE_EXTRA and value is not None
            ),
            RESET,
        )


def init(program_name, develop=False):
    for k, v in os.environ.items():
        print(k, v)

    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"handlers": ["console"], "level": "INFO"},
        "formatters": {
            "develop": {"()": DevelopFormatter},
        },
        "handlers": {
            "console": {
                "formatter": "std_out",
                "class": "logging.StreamHandler",
                "level": "INFO",
            }
        },
        "loggers": {
            "werkzeug": {"handlers": ["console"], "level": "WARN", "propagate": False},
            "app.api": {"handlers": ["console"], "level": "INFO", "propagate": False},
        },
    }

    if develop:
        logging_config["handlers"]["console"]["formatter"] = "develop"
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
    # TODO
    return logging.getLogger(name)


logger = get_logger(__name__)
original_argv = tuple(sys.argv)
