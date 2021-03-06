
from __future__ import print_function

# python standard library
import argparse
import os
import shutil
import sys
import ConfigParser
from collections import OrderedDict

# this package
from cameraobscura import BOLD, RESET, RED
import cameraobscura.set_logger
from cameraobscura.set_logger import set_logger
from cameraobscura.set_logger import EVENTLOG
from rate_vs_range import RateVsRangeTest
from cameraobscura import CameraobscuraError
from rvrconfiguration import AttenuationConfiguration
from rvrconfiguration import OtherConfiguration
from cameraobscura.utilities.query import QueryConfiguration
from cameraobscura.commands.ping.pingconfiguration import PingConfiguration
from cameraobscura.commands.iperf.Iperf import IperfConfiguration
from rvrconfiguration import DutEnum, ServerEnum
from cameraobscura.hosts.host import HostConfiguration
from cameraobscura.utilities.dump import DumpConfiguration

class ArgumentConstants(object):
    """
    Constants (primarily used to keep the tests in sync)
    """
    __slots__ = ()
    version = '2014.12.19'
    # defaults
    default_configuration = 'rvr_configuration.ini'
    default_path = 'rate_vs_range'

def parse_arguments(arguments=None):
    """
    Parses the command-line arguments

    :param:

     - `arguments`: list of command-line arguments (use if you don't want this to use sys.argv)

    :return: namespace of parsed arguments
    """
    parser = argparse.ArgumentParser(description='RVR Runner')
    # common arguments
    parser.add_argument('-v', '--version', help='Display the version number and quit',
                         action='version', version="%(prog)s {0}".format(ArgumentConstants.version))    

    parser.add_argument('--pudb', help='Enable the PUDB debugger default=%(default)s.',
                         action='store_true', default=False)
    parser.add_argument('--pdb', help='Enable the python debugger default=%(default)s.',
                         action='store_true', default=False)
    parser.add_argument('--debug', help='Enable debugging messages (default=%(default)s).',
                         action='store_true', default=False)
    parser.add_argument('--silent', help='Turn off non-error logging messages (default=%(default)s).',
                       action='store_true', default=False)
    subparsers = parser.add_subparsers(help='RVR Sub-Commands')    

    # fetch a sample configuration
    fetch = subparsers.add_parser('fetch')
    fetch.add_argument('-s', '--section', help="Section name to retrieve (defaults to all sections)",
                       default=None)
    fetch.set_defaults(subcommand=fetch_configuration)

    # run a configuration
    run = subparsers.add_parser('run')
    run.add_argument('configurations', default=[ArgumentConstants.default_configuration],
                     help="Configuration file(s) to use. default=%(default)s",
                     nargs='*')
    run.set_defaults(subcommand=run_configuration)
    return parser.parse_args(arguments)

def enable_debugging(args):
    """
    Enables pudb or pdb if requested

    :param:

      - `args`: namespace with pudb and pdb attributes

    :postcondition: debugger enabled if requested
    """
    if args.pudb:
        import pudb
        pudb.set_trace()
        return
    if args.pdb:
        import pdb
        pdb.set_trace()
    return

def get_examples():
    """
    gets the example strings from the configurations

    :return: generator of example configurations
    """
    examples = (AttenuationConfiguration(None),
                HostConfiguration(DutEnum.section, None),
                HostConfiguration(ServerEnum.section, None),
                IperfConfiguration(None),
                PingConfiguration(None),
                QueryConfiguration(None),
                DumpConfiguration(None),                
                OtherConfiguration(None))
    return examples

def fetch_configuration(args):
    """
    gets the default configuration and dumps it to the screen

    :param:

     - `args`: not currently used (TODO: make different samples)
    """
    examples = get_examples()
    
    if args.section is not None:
        for example in examples:
            if args.section == example.section:
                print(example.example)
                return

    # the whole shebang
    for example in examples:
        print(example.example.rstrip())
    return

def run_configuration(args):
    """
    Runs the AutomatedRVR.Test

    :param:

     - `args`: ConfigParser namespace with args.configurations filenames list
    """
    for filename in args.configurations:
        configuration = ConfigParser.SafeConfigParser()
        try:
            configuration.readfp(open(filename))
        except IOError as error:
            # file-name not found in current working directory
            print(error)
            print("try 'rvr fetch' or 'rvr help'")
            break
        test = Test(configuration)
        try:
            # this is only to replicate the original way it was being run
            # a better front end should probably replace this
            repetitions = test.configuration.other.repetitions + 1
            for repetition in xrange(1, repetitions):
                test.logger.info(BOLD + "**** Running repetition {0} of {1} ****".format(repetition,
                                                                        repetitions) + RESET)
                test()
                test.reset()
            # another quick hack
            source = cameraobscura.set_logger.EVENTLOG
            target_file = source
            target_path = os.path.join(test.result_location, 'logs')
            if not os.path.isdir(target_path):
                os.makedirs(target_path)
            count = len([name for name in os.listdir(target_path) if
                         os.path.isfile(name)])

            if count:
                base, ext = os.path.splitext(source)
                base = '{0}_{1}'.format(base, count)
                target_file = ''.join([base, ext])
            target = os.path.join(target_path, target_file)
            shutil.move(source, target)
        except CameraobscuraError as error:
            test.logger.error(error)
            dump_crash()
    return

def dump_crash():
    """
    creates a stack-trace file
    """
    # this should rarely (never?) be called
    import traceback
    separator = "*" * 20
    message = " Crash Report "
    header =  BOLD + RED + separator + message + separator + RESET
    footer = BOLD + RED + separator + separator + "*" * len(message) + RESET

    with open("crashreport.log", 'w') as f:
        f.write(header + "\n")        
        traceback.print_exc(file=f)
        f.write(footer + "\n")
    print("If you believe this is a program error,")
    print(("please save 'crashreport.log' and add it to a bug report on the"
           " bitbucket repository (https://bitbucket.org/allion_software_developers/cameraobscura)"
           " (along with the configuration and '{0}'").format(EVENTLOG))
    return

def main():
    """
    Parses the args then calls the sub-function retrieved
    """    
    arguments = parse_arguments()
    enable_debugging(arguments)
    set_logger(arguments)
    arguments.subcommand(arguments)
    return