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

The 'core' module provides useful functions that are used internally by
Sesh.
"""

from datetime import datetime
from getpass import getpass
from hashlib import sha256
import json
import os
import sqlite3
import sys

from dbman.config.base_config import (
    DBMAN_COOKIE_FILE, DBMAN_DB_PATH, DBMAN_SESSION_TIMEOUT
)
from dbman.enum import UserRole
from dbman.error import ExitCode, UserNotFound


def _login(username):
    kwargs = dict(new_session=True)
    user = _get_user(username, kwargs)
    password_hash = sha256(getpass().encode('utf-8')).hexdigest()
    password_check = _check_password(username, password_hash)

    if password_check:
        user._login()
        user_role = str(UserRole(user.role_id).name).capitalize()
        print(
            f"\nLogin successful for {username}\n"
            f"User Role is {user_role}\n\n"
        )


def _renew_session(args, kwargs):
    username = kwargs.get('username')
    token = kwargs.get('token')
    cmd = args.cmd
    target = _get_cmd_target(args)
    kwargs.update(new_session=False, cmd=args.cmd)
    user = _get_user(username, kwargs)
    user._renew_session(token, cmd, target)


def _logout(session):
    username = session.get('username')
    token = session.get('token')
    kwargs = dict(new_session=False, token=token)
    user = _get_user(username, kwargs)
    user._logout()

    print(
        f"\nUser {username} is now logged out.\n\n"
    )


def _get_user(username, kwargs):
    try:
        user_role = _check_user(username)
    except UserNotFound as e:
        print(e)
        sys.exit(ExitCode.EX_NOUSER)

    return user_role


def _check_user(username):
    conn = sqlite3.connect(DBMAN_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT "id", "role_id"
        FROM "user"
        WHERE "email_addr" =?
        """, (username,)
    )
    result = cursor.fetchone()

    try:
        user_role = result['role_id']
    except TypeError:
        raise UserNotFound(username)

    return user_role


def _check_password(username, password_hash):
    conn = sqlite3.connect(DBMAN_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT "password"
        FROM "user"
        WHERE "email_addr" =?
        """, (username,)
    )

    result = cursor.fetchone()
    password_check = result[0]

    if password_hash == password_check:
        return True
    else:
        print(f"\nLogin failed for {username}\n\n")
        return False


def _get_active_session(args):
    now = datetime.now().timestamp()
    custom_timeout = os.environ.get('DBMAN_SESSION_TIMEOUT')

    if custom_timeout:
        timeout = int(custom_timeout)
    else:
        timeout = DBMAN_SESSION_TIMEOUT

    if DBMAN_COOKIE_FILE.exists():
        with open(str(DBMAN_COOKIE_FILE), 'r') as f:
            cookie = json.load(f)
            username = cookie['username']
            token = cookie['token']

        conn = sqlite3.connect(
            DBMAN_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ls.time_last_cmd, ls.time_logout, u.email_addr
            FROM login_session ls
            JOIN user u
            WHERE ls.user_id = u.id
            AND ls.token =?
            """, (token,)
        )
        result = cursor.fetchone()
        time_last_cmd = result['time_last_cmd']
        time_logout = result['time_logout']
        email_addr = result['email_addr']

        if (username == email_addr and
                round(now - time_last_cmd) > timeout and time_logout is None):
            _logout(dict(username=username, token=token))
            active_session = None
        else:
            active_session = dict(username=username, token=token)
    else:
        active_session = None

    return active_session


def _get_cmd_target(args):
    cmd = args.cmd
    if cmd in ['delete', 'new', 'update']:
        target = args.target
    elif cmd == 'rent':
        target = args.action
    elif cmd == 'show':
        target = args.report
    else:
        target = None

    return target


def _show_account(args, kwargs):
    username = kwargs.get('username')
    user_role = _check_user(username)

    perm = False

    if user_role == UserRole.STAFF:
        perm = True

    if hasattr(args, 'student') and args.student == username:
        perm = True

    if not perm:
        print(
            f"\nYou must be logged-in as a Staff member in order to view "
            f"accounts other than your own.\n\n"
        )
        sys.exit(ExitCode.EX_NOPERM)


def _show_info(args, kwargs):
    kwargs['active_session'] = _get_active_session(args)


def _show_instrument(args, kwargs):
    pass


def _show_schedule(args, kwargs):
    pass


def _show_user(args, kwargs):
    pass
