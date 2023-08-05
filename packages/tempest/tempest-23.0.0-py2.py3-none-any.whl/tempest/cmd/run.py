# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Runs tempest tests

This command is used for running the tempest tests

Test Selection
==============
Tempest run has several options:

* ``--regex/-r``: This is a selection regex like what stestr uses. It will run
  any tests that match on re.match() with the regex
* ``--smoke/-s``: Run all the tests tagged as smoke
* ``--black-regex``: It allows to do simple test exclusion via passing a
  rejection/black regexp

There are also the ``--blacklist-file`` and ``--whitelist-file`` options that
let you pass a filepath to tempest run with the file format being a line
separated regex, with '#' used to signify the start of a comment on a line.
For example::

    # Regex file
    ^regex1 # Match these tests
    .*regex2 # Match those tests

These arguments are just passed into stestr, you can refer to the stestr
selection docs for more details on how these operate:
http://stestr.readthedocs.io/en/latest/MANUAL.html#test-selection

You can also use the ``--list-tests`` option in conjunction with selection
arguments to list which tests will be run.

You can also use the ``--load-list`` option that lets you pass a filepath to
tempest run with the file format being in a non-regex format, similar to the
tests generated by the ``--list-tests`` option. You can specify target tests
by removing unnecessary tests from a list file which is generated from
``--list-tests`` option.

Test Execution
==============
There are several options to control how the tests are executed. By default
tempest will run in parallel with a worker for each CPU present on the machine.
If you want to adjust the number of workers use the ``--concurrency`` option
and if you want to run tests serially use ``--serial/-t``

Running with Workspaces
-----------------------
Tempest run enables you to run your tempest tests from any setup tempest
workspace it relies on you having setup a tempest workspace with either the
``tempest init`` or ``tempest workspace`` commands. Then using the
``--workspace`` CLI option you can specify which one of your workspaces you
want to run tempest from. Using this option you don't have to run Tempest
directly with you current working directory being the workspace, Tempest will
take care of managing everything to be executed from there.

Running from Anywhere
---------------------
Tempest run provides you with an option to execute tempest from anywhere on
your system. You are required to provide a config file in this case with the
``--config-file`` option. When run tempest will create a .stestr
directory and a .stestr.conf file in your current working directory. This way
you can use stestr commands directly to inspect the state of the previous run.

Test Output
===========
By default tempest run's output to STDOUT will be generated using the
subunit-trace output filter. But, if you would prefer a subunit v2 stream be
output to STDOUT use the ``--subunit`` flag

Combining Runs
==============

There are certain situations in which you want to split a single run of tempest
across 2 executions of tempest run. (for example to run part of the tests
serially and others in parallel) To accomplish this but still treat the results
as a single run you can leverage the ``--combine`` option which will append
the current run's results with the previous runs.
"""

import os
import sys

from cliff import command
from oslo_serialization import jsonutils as json
import six
from stestr import commands

from tempest import clients
from tempest.cmd import cleanup_service
from tempest.cmd import init
from tempest.cmd import workspace
from tempest.common import credentials_factory as credentials
from tempest import config

if six.PY2:
    # Python 2 has not FileNotFoundError exception
    FileNotFoundError = IOError

CONF = config.CONF
SAVED_STATE_JSON = "saved_state.json"


class TempestRun(command.Command):

    def _set_env(self, config_file=None):
        if config_file:
            if os.path.exists(os.path.abspath(config_file)):
                CONF.set_config_path(os.path.abspath(config_file))
            else:
                raise FileNotFoundError(
                    "Config file: %s doesn't exist" % config_file)

        # NOTE(mtreinish): This is needed so that stestr doesn't gobble up any
        # stacktraces on failure.
        if 'TESTR_PDB' in os.environ:
            return
        else:
            os.environ["TESTR_PDB"] = ""
        # NOTE(dims): most of our .stestr.conf try to test for PYTHON
        # environment variable and fall back to "python", under python3
        # if it does not exist. we should set it to the python3 executable
        # to deal with this situation better for now.
        if six.PY3 and 'PYTHON' not in os.environ:
            os.environ['PYTHON'] = sys.executable

    def _create_stestr_conf(self):
        top_level_path = os.path.dirname(os.path.dirname(__file__))
        discover_path = os.path.join(top_level_path, 'test_discover')
        file_contents = init.STESTR_CONF % (discover_path, top_level_path)
        with open('.stestr.conf', 'w+') as stestr_conf_file:
            stestr_conf_file.write(file_contents)

    def take_action(self, parsed_args):
        if parsed_args.config_file:
            self._set_env(parsed_args.config_file)
        else:
            self._set_env()
        # Workspace execution mode
        if parsed_args.workspace:
            workspace_mgr = workspace.WorkspaceManager(
                parsed_args.workspace_path)
            path = workspace_mgr.get_workspace(parsed_args.workspace)
            if not path:
                sys.exit(
                    "The %r workspace isn't registered in "
                    "%r. Use 'tempest init' to "
                    "register the workspace." %
                    (parsed_args.workspace, workspace_mgr.path))
            os.chdir(path)
            if not os.path.isfile('.stestr.conf'):
                self._create_stestr_conf()
        # local execution with config file mode
        elif parsed_args.config_file and not os.path.isfile('.stestr.conf'):
            self._create_stestr_conf()
        elif not os.path.isfile('.stestr.conf'):
            print("No .stestr.conf file was found for local execution")
            sys.exit(2)
        if parsed_args.state:
            self._init_state()

        regex = self._build_regex(parsed_args)
        return_code = 0
        if parsed_args.list_tests:
            return_code = commands.list_command(
                filters=regex, whitelist_file=parsed_args.whitelist_file,
                blacklist_file=parsed_args.blacklist_file,
                black_regex=parsed_args.black_regex)

        else:
            serial = not parsed_args.parallel
            return_code = commands.run_command(
                filters=regex, subunit_out=parsed_args.subunit,
                serial=serial, concurrency=parsed_args.concurrency,
                blacklist_file=parsed_args.blacklist_file,
                whitelist_file=parsed_args.whitelist_file,
                black_regex=parsed_args.black_regex,
                load_list=parsed_args.load_list, combine=parsed_args.combine)
            if return_code > 0:
                sys.exit(return_code)
        return return_code

    def get_description(self):
        return 'Run tempest'

    def _init_state(self):
        print("Initializing saved state.")
        data = {}
        self.global_services = cleanup_service.get_global_cleanup_services()
        self.admin_mgr = clients.Manager(
            credentials.get_configured_admin_credentials())
        admin_mgr = self.admin_mgr
        kwargs = {'data': data,
                  'is_dry_run': False,
                  'saved_state_json': data,
                  'is_preserve': False,
                  'is_save_state': True}
        for service in self.global_services:
            svc = service(admin_mgr, **kwargs)
            svc.run()

        with open(SAVED_STATE_JSON, 'w+') as f:
            f.write(json.dumps(data, sort_keys=True,
                               indent=2, separators=(',', ': ')))

    def get_parser(self, prog_name):
        parser = super(TempestRun, self).get_parser(prog_name)
        parser = self._add_args(parser)
        return parser

    def _add_args(self, parser):
        # workspace args
        parser.add_argument('--workspace', default=None,
                            help='Name of tempest workspace to use for running'
                                 ' tests. You can see a list of workspaces '
                                 'with tempest workspace list')
        parser.add_argument('--workspace-path', default=None,
                            dest='workspace_path',
                            help="The path to the workspace file, the default "
                                 "is ~/.tempest/workspace.yaml")
        # Configuration flags
        parser.add_argument('--config-file', default=None, dest='config_file',
                            help='Configuration file to run tempest with')
        # test selection args
        regex = parser.add_mutually_exclusive_group()
        regex.add_argument('--smoke', '-s', action='store_true',
                           help="Run the smoke tests only")
        regex.add_argument('--regex', '-r', default='',
                           help='A normal stestr selection regex used to '
                                'specify a subset of tests to run')
        parser.add_argument('--black-regex', dest='black_regex',
                            help='A regex to exclude tests that match it')
        parser.add_argument('--whitelist-file', '--whitelist_file',
                            help="Path to a whitelist file, this file "
                            "contains a separate regex on each "
                            "newline.")
        parser.add_argument('--blacklist-file', '--blacklist_file',
                            help='Path to a blacklist file, this file '
                                 'contains a separate regex exclude on '
                                 'each newline')
        parser.add_argument('--load-list', '--load_list',
                            help='Path to a non-regex whitelist file, '
                                 'this file contains a separate test '
                                 'on each newline. This command '
                                 'supports files created by the tempest '
                                 'run ``--list-tests`` command')
        # list only args
        parser.add_argument('--list-tests', '-l', action='store_true',
                            help='List tests',
                            default=False)
        # execution args
        parser.add_argument('--concurrency', '-w',
                            type=int, default=0,
                            help="The number of workers to use, defaults to "
                                 "the number of cpus")
        parallel = parser.add_mutually_exclusive_group()
        parallel.add_argument('--parallel', dest='parallel',
                              action='store_true',
                              help='Run tests in parallel (this is the'
                                   ' default)')
        parallel.add_argument('--serial', '-t', dest='parallel',
                              action='store_false',
                              help='Run tests serially')
        parser.add_argument('--save-state', dest='state',
                            action='store_true',
                            help="To save the state of the cloud before "
                                 "running tempest.")
        # output args
        parser.add_argument("--subunit", action='store_true',
                            help='Enable subunit v2 output')
        parser.add_argument("--combine", action='store_true',
                            help='Combine the output of this run with the '
                                 "previous run's as a combined stream in the "
                                 "stestr repository after it finish")

        parser.set_defaults(parallel=True)
        return parser

    def _build_regex(self, parsed_args):
        regex = None
        if parsed_args.smoke:
            regex = ['smoke']
        elif parsed_args.regex:
            regex = parsed_args.regex.split()
        return regex
