"""For logging"""

import logging
import datetime

import daiquiri
import daiquiri.formatter

daiquiri.setup(
    level=logging.DEBUG,
    outputs=(
        daiquiri.output.File("logs/errors.log", level=logging.ERROR),
        daiquiri.output.TimedRotatingFile(
            "logs/logs.log", level=logging.DEBUG, interval=datetime.timedelta(hours=1)
        ),
        daiquiri.output.Stream(
            formatter=daiquiri.formatter.ColorFormatter(
                fmt="%(asctime)s [PID %(process)d] [%(levelname)s] "
                "%(name)s -> %(message)s"
            )
        ),
    ),
)

logger = daiquiri.getLogger(__name__)
