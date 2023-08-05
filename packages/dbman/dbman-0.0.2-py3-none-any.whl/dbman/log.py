"""
dbman is a tool for generating data and managing relational databases.
Copyright (C) 2020  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com

The log module reads-in the dbman_logging.json file and sets up logging for
Sesh.

The Sesh log file is located at ~/.local/log/dbman.log

There are no current provisions for modifting the logging configuration, but
we hope to offer this functioanlity in a future release.
"""

import json
import logging
import logging.config
import os
import sys

from dbman.config.base_config import DBMAN_LOG_CONFIG, DBMAN_LOG_FILE, DBMAN_LOG_LEVEL
from dbman.error import ExitCode


def _get_logging_config(env_log_level='DBMAN_LOG_LEVEL',
                        env_log_config='DBMAN_LOG_CONFIG',
                        env_log_file='DBMAN_LOG_FILE'):
    """Setup logging configuration."""
    value = os.getenv(env_log_config)
    if value:
        log_config_path = value
    else:
        log_config_path = DBMAN_LOG_CONFIG

    try:
        with open(log_config_path, 'rt') as f:
            logging_config = json.load(f)
    except OSError:
        print(f"Failed to open dbman logging configuration file at "
              f"{log_config_path}\nExiting...\n\n")
        sys.exit(ExitCode.EX_NOINPUT)

    value = os.getenv(env_log_file)
    if value:
        dbman_log_file = value
    else:
        dbman_log_file = DBMAN_LOG_FILE
    logging_config['handlers']['default_handler']['filename'] = dbman_log_file

    value = os.getenv(env_log_level)
    if value:
        dbman_log_level = value
    else:
        dbman_log_level = DBMAN_LOG_LEVEL
    logging_config['loggers']['dbman']['level'] = dbman_log_level

    return logging_config


logging.config.dictConfig(_get_logging_config())


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)

    return logger
