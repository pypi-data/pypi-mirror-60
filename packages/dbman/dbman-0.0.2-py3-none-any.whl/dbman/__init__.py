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


    dbman [args] [<command>] [<args>]

"""

from dbman import api
from dbman.cli import parser
from dbman.config.base_config import DBMAN_DB_PATH
from dbman.error import ExitCode
from dbman.log import get_logger

logger = get_logger(__name__)


def main():
    """Run `dbman` command
    If the user calls `dbman --help`, or `dbman COMMAND` with out the expected
    COMMAND arguments, the parser will catch this in the parser.parse_args()
    method and then print the Help and exit before going any further
    in the main() function.

    The 'check' that is performed in main() ensures that if the user runs
    `dbman` without *any* arguments, the Help will still be displayed.
    """
    """Setup logging configuration."""
    args = parser.parse_args() or None
    logger.info(f"cli args: {vars(args)}")

    if len(vars(args)) > 0:
        active_session = api.check_for_session(args)
        if active_session:
            api.renew_session(args, active_session)
        if args.cmd == 'admin' and not DBMAN_DB_PATH.exists():
            try:
                kwargs = dict(init=True)
                api.admin(args, kwargs)
            except SystemExit as e:
                return e.code
            else:
                return ExitCode.EX_SUCCESS
        if (
            args.cmd == 'show' and
            args.report == 'account' and
            not (args.month or args.period)
        ):
            parser.error(
                '\nNo time period requested for this report. Please use\n'
                '-m MONTH or -p START_DATE END_DATE\n'
            )
        elif args.cmd != 'login' and active_session:
            try:
                kwargs = active_session
                getattr(api, args.cmd)(args, kwargs)
            except SystemExit as e:
                return e.code
            else:
                return ExitCode.EX_SUCCESS
        elif args.cmd == 'login' and not active_session:
            try:
                api.login(args)
            except SystemExit as e:
                return e.code
            else:
                return ExitCode.EX_SUCCESS
        elif args.cmd == 'login' and active_session:
            username = active_session.get('username')
            print(
                f"\nThe user {username} is currently logged-in.\n"
                f"Please log that user out first and then try logging in "
                f"again.\n\n"
            )
        else:
            print(
                f"\nYou must be logged-in before executing the '{args.cmd}' "
                f"command.\n\n"
            )
    else:
        parser.print_help()
        return ExitCode.EX_USAGE
