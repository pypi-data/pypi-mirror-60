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

The constants module provides default values and other constants used by Sesh.
Many of these constants may be overriden in the Sesh config.yaml file.
"""

from pathlib import Path

_user_home = Path.home()
_log_dir = Path(_user_home).joinpath('.local', 'log')
_data_dir = Path(_user_home).joinpath('.local', 'var')

_log_dir.mkdir(parents=True, exist_ok=True)
_data_dir.mkdir(parents=True, exist_ok=True)

DBMAN_BASE_PATH = Path(__file__).parents[1]

# Logging
DBMAN_LOG_FILE = Path(_user_home).joinpath(_log_dir, 'dbman.log')
DBMAN_LOG_CONFIG = Path(DBMAN_BASE_PATH).joinpath(
    'config', 'dbman_logging.json'
)
DBMAN_LOG_LEVEL = 'INFO'

# Database
DBMAN_DB_PATH = Path(_user_home).joinpath(_data_dir, 'dbman.db')
DBMAN_ADMIN_FILE = Path(_user_home).joinpath(_data_dir, 'admin.text')
DBMAN_COOKIE_FILE = Path(_user_home).joinpath(_data_dir, 'dbman_cookie')

DBMAN_SESSION_TIMEOUT = 300
