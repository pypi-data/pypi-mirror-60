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

The error module provides custom DBMan Error Classes, as well as an ExitCode
class that supplies exit code values used when exiting the DBMan program.
Errror messages are available in the DBMan log file, which is located at
~/.local/log/dbman.log by default.

In bash, the exit code can be retrieved in the usual manner, by querying
$? after the program exits.

Exit codes for many (most) systems are usually 0 for success and 1 for
general failure.

BSD has attempted to standardize exit codes. These values are usually defined
in /usr/include/sysexits.h on Linux systems.

The codes and their meanings can also be found online at:

https://man.openbsd.org/sysexits.3
"""

from enum import IntEnum


class ExitCode(IntEnum):
    """Enumeration of exit codes.

    This class implements POSIX error codes, as found in
    /usr/include/sysexits.h on the Linux platform and
    described in the manual page for sysexit on BSD systems,
    including Darwin (macOS).

    Additional information is availble from The Linux Documnetation Project
    at http://tldp.org/LDP/abs/html/exitcodes.html
    """
    EX_SUCCESS = 0  # command exits successfully
    EX_GENERAL = 1  # catchall for general errors
    EX_USAGE = 64  # command line usage error
    EX_DATAERR = 65  # data format error
    EX_NOINPUT = 66  # cannot open input
    EX_NOUSER = 67  # addressee unknown
    EX_NOHOST = 68  # host name unknown
    EX_UNAVAILABLE = 69  # service unavailable
    EX_SOFTWARE = 70  # internal software error
    EX_OSERR = 71  # system error (e.g., can't fork)
    EX_OSFILE = 72  # critical OS file missing
    EX_CANTCREAT = 73  # can't create (user) output file
    EX_IOERR = 74  # input/output error
    EX_TEMPFAIL = 75  # temp failure; user is invited to retry
    EX_PROTOCOL = 76  # remote error in protocol
    EX_NOPERM = 77  # permission denied
    EX_CONFIG = 78  # configuration error
    EX_SIGINT = 130  # keyboard interrupt


class DBManError(Exception):
    """Base class for exceptions in this package."""
    pass


class CmdUsageError(DBManError):
    """docstring for CmdUsageError"""

    def __init__(self, report):
        self.message = (
            f"\nUnknown 'show' commad: {report}.\n\n"
            f"Please run `dbman show --help` for a list of availble reports."
            f"\n\n"
        )

    def __str__(self):
        return self.message


class ConfigError(DBManError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class UserNotFound(DBManError):
    """docstring for UserNotFound"""

    def __init__(self, email_addr):
        self.message = (
            f"\nNo user was found with the email address {email_addr}.\n\n"
            f"Please try another email address or ask your administrator to\n"
            f"create an account for you.\n\n"
        )

    def __str__(self):
        return self.message
