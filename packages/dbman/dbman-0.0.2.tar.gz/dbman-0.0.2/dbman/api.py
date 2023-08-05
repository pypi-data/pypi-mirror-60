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

The examples given for the functions below are shown in the context of CLI
commands. However this module is intended to provide an API that may be
used by other interfaces in the future.

The args parameter that is passed into each of these functions is expected
to be a Namepace object, similar to that created by the argparse module in the
Standard Library. For more information on this, please see:

https://docs.python.org/3/library/argparse.html#the-namespace-object
"""

import sys

from dbman import core
from dbman.config.base_config import DBMAN_COOKIE_FILE, DBMAN_DB_PATH
from dbman.enum import UserRole
from dbman.error import CmdUsageError, ExitCode

__all__ = ['admin', 'delete', 'login', 'logout', 'new', 'show', 'update']


def check_for_session(args):
    return core._get_active_session(args)


def admin(args, kwargs=None):
    """Administer the Sesh database.

    Args:
        --init-db:
            Initialize a new database with default values. Any existing
            database for Sesh will be deleted!

        --load-sample-data:
            Add a reasonably-sized data set of example
            data, for use in testing, or for exploring Sesh without
            needing to set up a whole lot from the start. The only table
            that will not be populated is the login_session table.
            See the _load_sample_data() function in the init_db module for
            the data set that is loaded.

    Examples:
        dbman admin --init-db

        dbman admin --load-sample-data

        dbman admin --init-db --load-sample-data

    NOTE:
        You must be logged in as a user in a 'Staff' role in order to issue
        these commands.
    """
    first_run = kwargs.get('init')
    username = kwargs.get('username')

    if first_run:
        user_role = None
    else:
        user_role = core._check_user(username)

    if user_role != UserRole.STAFF and DBMAN_DB_PATH.exists():
        print(
            f"\nYou must be logged-in as a Staff member in order to run "
            f"'admin' commands.\n\n"
        )
        sys.exit(ExitCode.EX_NOPERM)

    if args.init_db:
        _init_db()
        if DBMAN_COOKIE_FILE.exists():
            DBMAN_COOKIE_FILE.unlink()

    if args.load_sample_data:
        _load_sample_data()


def delete(args, kwargs=None):
    pass


def login(args, kwargs=None):
    """Login to Sesh.

    The user must already have a login account. New accounts must be created
    by a user in a 'Staff' role.

    Once logged-in, the user will remain logged-in until they logout, or until
    five minutes have passed since they last issued a command.

    Only one user may be logged in at a time. Multiple users may be supported
    in a future release.

    Args:
        username:
            The email address of the user to logout.

    Examples:
        dbman login admin@example.com
    """
    core._login(args.username)


def renew_session(args, kwargs):
    core._renew_session(args, kwargs)


def logout(args, kwargs=None):
    """Logout of Sesh.

    Args:
        username: The email address of the user to logout.

    Examples:
        dbman logout admin@example.com
    """
    core._logout(kwargs)


def new(args, kwargs=None):
    logged_in_user = kwargs.get('username')
    print(
        f"\n{logged_in_user} is creating new target: {args.target}\n\n"
    )
    pass


def rent():
    pass


def show(args, kwargs=None):
    if args.report == 'account':
        core._show_account(args, kwargs)
    elif args.report == 'info':
        core._show_info(args, kwargs)
    elif args.report == 'instrument':
        core._show_instrument(args, kwargs)
    elif args.report == 'schedule':
        core._show_schedule(args, kwargs)
    else:
        raise CmdUsageError(args.report)
        sys.exit(ExitCode.EX_USAGE)


def update(args, kwargs=None):
    pass
