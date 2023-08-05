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

This module should handle all of the command-line parsing and
invoke the correct command in the api module.
"""

import argparse

from dbman.__version__ import __version__


# create the top-level parser
parser = argparse.ArgumentParser(
    prog='dbman',
    description='Use dbman to manage Music Center classes and rentals.',
    conflict_handler='resolve',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='\n \n',
)

parser.add_argument(
    '--version',
    action='version',
    version='%(prog)s ' + f'version { __version__}'
)

# Add subparser below for each dbman command
subparsers = parser.add_subparsers(
    title='dbman commands',
)


# create the parser for the "admin" command
parser_admin = subparsers.add_parser(
    'admin',
    help=(
        'Perform administrative functions on the Sesh database\n'
        'itself. A Staff member login is required to perform\n'
        'these actions.\n\n'
    )
)

parser_admin.add_argument(
    '--init-db',
    action='store_true',
    dest='init_db',
    help='Initialize a new database. Any existing database will be deleted!'
)

parser_admin.add_argument(
    '--load-sample-data',
    action='store_true',
    dest='load_sample_data',
    help='Load some sample data into the database.'
)

parser_admin.set_defaults(cmd='admin')


# create the parser for the "delete" command
parser_delete = subparsers.add_parser(
    'delete',
    help='help for delete command\n\n'
)

parser_delete.add_argument(
    'target',
    choices=[
        'classroom',
        'instrument',
        'role',
        'user',
    ],
)

parser_delete.set_defaults(cmd='delete')


# create the parser for the "login" command
parser_login = subparsers.add_parser(
    'login',
    help=(
        'Login to Sesh\n\n'
        'The user must already have a login account.\n'
        'New accounts must be created by a user in a \'Staff\' role.\n'
        'Once logged-in, the user will remain logged-in until they\n'
        'logout, or until five minutes have passed since they last\n'
        'issued a command.\n\n'
    )
)

parser_login.add_argument(
    'username',
    help='email address of user to login'
)

parser_login.set_defaults(cmd='login')


# create the parser for the "logout" command
parser_logout = subparsers.add_parser(
    'logout',
    help='help for logout command'
)

parser_logout.set_defaults(cmd='logout')


# create the parser for the "new" command
parser_new = subparsers.add_parser(
    'new',
    help='help for new command'
)

parser_new.add_argument(
    'target',
    choices=[
        'classroom',
        'instrument',
        'role',
        'user',
    ],
)

parser_new.set_defaults(cmd='new')


# create the parser for the "update" command
parser_update = subparsers.add_parser(
    'update',
    help='help for update command'
)

parser_update.add_argument(
    'target',
    choices=[
        'classroom',
        'instrument',
        'role',
        'user',
    ],
)

parser_update.set_defaults(cmd='update')


# create the parser for the "rent" command
parser_rent = subparsers.add_parser(
    'rent',
    help='help for rent command'
)

parser_rent.add_argument(
    'action',
    choices=[
        'start',
        'stop',
    ],
)

parser_rent.set_defaults(cmd='rent')


# create the parser for the "show" command
parser_show = subparsers.add_parser(
    'show',
    formatter_class=argparse.RawTextHelpFormatter,
    help='help for the show command'
)

filter_group = parser_show.add_mutually_exclusive_group()
time_group = parser_show.add_mutually_exclusive_group()

parser_show.add_argument(
    'report',
    choices=[
        'account',
        'info',
        'instrument',
        'schedule',
    ],
    help=(
        'The type of report to show.\n'
    )
)


filter_group.add_argument(
    '-a', '--all',
    action='store_true',
    dest='all',
    help=(
        'Show report for all account(s), instrument(s),\n'
        'schedule(s), or user(s).\n'
        'This option cannot be used with the [-u, --user] option\n\n'
    )
)


time_group.add_argument(
    '-m', '--month',
    action='store',
    dest='month',
    # nargs=1,
    help=(
        'This option is only useful for the \'account\' and\n'
        '\'schedule\' reports.\n'
        'Show the report for a particular month.\n'
        'MONTH should be in the format MM-YYYY.\n\n'
    )
)


time_group.add_argument(
    '-p', '--period',
    action='store',
    dest='period',
    nargs=2,
    metavar=('START_DATE', 'END_DATE'),
    help=(
        'This option is only useful for the \'account\' and\n'
        '\'schedule\' reports.\n'
        'Show the report for an arbitrary period of days.\n'
        'START_DATE and END_DATE should each be in the format\n'
        'MM-DD-YYYY.\n\n'
    )
)


filter_group.add_argument(
    '-s', '--student',
    action='store',
    dest='student',
    metavar='USERNAME',
    help=(
        'Show the report for a particular user.\n'
        'USERNAME should each be the email address for the user.\n'
        'This option cannot be used with the [-a, --all] option\n\n'
    )
)


parser_show.add_argument(
    '-t', '--tag',
    action='store',
    dest='tag',
    metavar='TAG',
    help=(
        'This option is REQUIRED for the \'instrument\' report if the\n'
        '[-a, --all] option is not used.\n'
        'Show the report for a particular inventory tag.\n'
        'TAG should each be the inventory tag for the instrument.\n\n'
    )
)


parser_show.add_argument(
    '-v', '--verbose',
    action='store_true',
    dest='verbose',
    help=(
        'This option adds additional fields to the account report\n'
        'Additional fields include \'Instrument\', \'Recorded?\', \n'
        'and \'Canceled\'.'
    )
)


parser_show.add_argument(
    '--csv',
    action='store_true',
    dest='csv',
    help='Save report to a CSV file.'
)

parser_show.add_argument(
    '--json',
    action='store_true',
    dest='json',
    help='Save report to a JSON file.'
)

parser_show.set_defaults(cmd='show')
