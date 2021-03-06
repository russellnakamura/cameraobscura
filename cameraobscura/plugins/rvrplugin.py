
# python standard library
from ConfigParser import ConfigParser
from collections import OrderedDict
import sys

# the ape needs this, I don't know if I can get around this
try:
    from ConfigObj import ConfigObj
except ImportError:
    pass

# cameraobscura
from cameraobscura.ratevsrange.rvrconfiguration import OtherEnum as RVRConstants
from cameraobscura.ratevsrange.rvrconfiguration import AttenuationEnum as AttenuationConstants
from cameraobscura.ratevsrange.rvrconfiguration import AttenuationConfiguration
from cameraobscura.ratevsrange.rvrconfiguration import TrafficEnum as TrafficConstants
from cameraobscura.hosts.host import HostEnum as HostConstants
from cameraobscura.utilities.configurationadapter import ConfigurationAdapter
from cameraobscura.commands.iperf.Iperf import IperfEnum, IperfConfiguration
from cameraobscura.commands.iperf.iperfsettings import (IperfServerSettings,
                                                        IperfClientSettings)

# the ape package
from theape import BasePlugin, BaseConfiguration, SubConfiguration
from theape.parts.iperf.iperfsettings import iperf_checks
from theape.parts.iperf.iperfsettings import iperf_configspec as ape_iperf_configspec

configuration = """
  [[RVR]]
  # these first two lines are needed by the ape
  plugin = RVR
  module = cameraobscura.plugins.rvrplugin

  """

rvr_configuration_specification = """
[attenuation]
start = integer(default=0)
stop = integer(default=9223372036854775807)
name = option('mockattenuator', 'weinschelp', default='weinschelp')
control_ip = string
step_sizes = int_list(default=list(1,))
step_change_thresholds = int_list(default=None)

[dut]
username = string
control_ip = string
test_ip = string
password = string(default=None)
connection_type = string(default='ssh')
timeout = float(default=1)
prefix = string(default=None)
operating_system = option('cygwin', 'linux', default='linux')

[server]
username = string
control_ip = string
test_ip = string
password = string(default=None)
connection_type = string(default='ssh')
timeout = float(default=1)
prefix = string(default=None)
operating_system = option('cygwin', 'linux', default='linux')

[iperf]
direction = force_list(default=list('downstream', 'upstream'))
parallel = integer(default=None)
"""

sections = OrderedDict()
sections['name'] = '{bold}RVR{reset} -- a bandwith with attenuation measurer'
sections['description'] = '{bold}RVR{reset} runs the CameraObscura rate-vs-range implementation.'
sections['configuration'] = configuration
#sections['see also'] = ''
sections['options'] = """
The configuration options --

    {bold}end{reset} : an absolute time given as a time-stamp that can be interpreted by `dateutil.parser.parse`. This is for the cases where you have a specific time that you want the sleep to end.

    {bold}total{reset} : a relative time given as pairs of '<amount> <units>' -- e.g. '3.4 hours'. Most units only use the first letter, but since `months` and `minutes` both start with `m`, you have to use two letters to specify them. The sleep will stop at the start of the sleep + the total time given.

    {bold}interval{reset} : The amount of time beween reports of the time remaining (default = 1 second). Use the same formatting as the `total` option.

    {bold}verbose{reset} : If True (the default) then report time remaining at specified intervals while the sleep runs.

One of {bold}end{reset} or {bold}total{reset} needs to be specified. Everything else is optional.
"""
sections['author'] = 'ape'

class RVR(BasePlugin):
    """
    A plugin for the RVR front-end
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor for RVR Plugin
        """
        super(RVR, self).__init__(*args, **kwargs)
        self._attenuation_configuration = None
        return

    @property
    def attenuation_configuration(self):
        """
        Builder for the AttenuationPluginConfiguration
        """
        return

    def fetch_config(self):
        """
        prints a config-file sample
        """
        print(self.attenuation_configuration.sample)
        return

    @property
    def sections(self):
        """
        Help dictionary
        """
        if self._sections is None:
            self._sections = sections
        return self._sections

    @property
    def product(self):
        """
        A built RVR object

        :return: RVR
        """
        if self._product is None:
            end = self.subsection[END_OPTION]
            total = self.subsection[TOTAL_OPTION]
            interval = self.subsection[INTERVAL_OPTION]

            if interval != 1:
                interval = interval.total_seconds()
            verbose = self.subsection[VERBOSE_OPTION]
            self._product = TheBigSleep(end=end,
                                        total=total,
                                        interval=interval,
                                        verbose=verbose)
        return self._product
# end RVRPlugin

other_configuration_configspec = """
{folder_option} = string(default='{folder}')
{test_name} = string(default='{name}')
{repetitions_option} = integer(default={repetitions})
{recovery_option} = float(default={recovery})
""".format(folder_option=RVRConstants.result_location,
           folder=RVRConstants.default_result_location,
           test_name=RVRConstants.test_name,
           name=RVRConstants.default_test_name,
           repetitions_option=RVRConstants.repetitions,
           repetitions=RVRConstants.default_repetitions,
           recovery_option=RVRConstants.recovery_time,
           recovery=RVRConstants.default_recovery_time)

class RVRConfiguration(BaseConfiguration):
    """
    The Main configuration 
    """
    def __init__(self, *args, **kwargs):
        """
        RVRConfiguration (sets allow extras to True)
        """
        super(RVRConfiguration, self).__init__(*args, **kwargs)
        self.allow_extras = True
        self._attenuation = None
        self._dut = None
        self._server = None
        self._iperf = None
        return
    
    @property
    def configspec_source(self):
        """String configuration specification"""
        if self._configspec_source is None:
            self._configspec_source = other_configuration_configspec            
        return self._configspec_source

    @property
    def product(self):
        """
        the callable product
        """

    @property
    def attenuation(self):
        """
        An AttenuationPluginConfiguration        
        """
        if self._attenuation is None:
            self._attenuation = AttenuationPluginConfiguration(source=self.configuration,
                                                         section_name=AttenuationConstants.section)
        return self._attenuation

    @property
    def dut(self):
        """
        Host Configuration for the dut
        """
        if self._dut is None:
            self._dut = HostConfiguration(source=self.configuration,
                                          section_name='dut')
        return self._dut

    @property
    def server(self):
        """
        Host Configuration for the server
        """
        if self._server is None:
            self._server = HostConfiguration(source=self.configuration,
                                             section_name='server')
        return self._server

    @property
    def iperf(self):
        """
        Iperf Configuration
        """
        if self._iperf is None:
            self._iperf = IperfPluginConfiguration(source=self.configuration,
                                             section_name='iperf')          
        return self._iperf

    def check_rep(self):
        """
        calls parent check_rep then the sub-configurations check_rep
        """
        super(RVRConfiguration, self).check_rep()
        self.attenuation.check_rep()
        self.dut.check_rep()
        self.server.check_rep()
        self.iperf.check_rep()
        return

attenuation_configspec = """
control_ip = string
start = integer(default=0)
stop = integer(default={maxint})
name = option('weinschelp', 'mockattenuator', 'MockAttenuator', 'WeinschelP', default='WeinschelP')s
step_sizes = int_list(default=list(1,))
step_change_thresholds = int_list(default=None)
reversal_limit = integer(default=None)
""".format(maxint=sys.maxint)

class AttenuationPluginConfiguration(SubConfiguration):
    """
    A sub-configuration for the attenuation section
    """
    def __init__(self, *args, **kwargs):
        super(AttenuationPluginConfiguration, self).__init__(*args,
                                                             **kwargs)
        self._configuration = None
        self._attenuation_configuration = None
        self._adapter = None
        return

    @property
    def adapter(self):
        """
        Mapping config obj to the Configuration Adapter
        """
        if self._adapter is None:
            # there is an unfortunate inconsistency in the camera obscura's configuration
            config = ConfigParser()
            section = 'attenuation'
            config.add_section(section)
            lists = 'step_sizes step_change_thresholds step_list'.split()
            to_recast = (name for name in lists if name in self.configuration)
            for name in to_recast:
                if name in self.configuration and self.configuration[name] is not None:
                    self.configuration[name] = ' '.join(str(item) for item in self.configuration[name])
            for name, value in self.configuration.iteritems():
                # unfortunately the ConfigParser will only accept strings
                config.set(section, name, str(value))
            self._adapter = ConfigurationAdapter(config)
        return self._adapter

    @property
    def attenuation_configuration(self):
        """
        A built cameraobscura AttenuationConfiguration
        """
        if self._attenuation_configuration is None:            
            self._attenuation_configuration = AttenuationConfiguration(self.adapter)
        return self._attenuation_configuration               
    
    @property
    def configspec_source(self):
        """
        string attenuation configuration specification
        """
        if self._configspec_source is None:
            self._configspec_source = attenuation_configspec
        return self._configspec_source

query_configspec = """
filename = string(default='query.csv')
timeout = float(default=10)
trap_errors = boolean(default=True)
__many__ = list(min=2, max=2)
"""

class QueryPluginConfiguration(SubConfiguration):
    """
    A configuration for the queries
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor to set up the sub-configuration
        """
        super(QueryPluginConfiguration, self).__init__(*args,
                                                 **kwargs)
        self._query_configuration = None
        self._adapter is None
        return

    @property
    def adapter(self):
        """
        Mapping config obj to the Configuration Adapter
        """
        if self._adapter is None:
            config = ConfigParser()
            section = 'query'
            config.add_section(section)
            self._adapter = ConfigurationAdapter(config)
        return self._adapter

    @property
    def query_configuration(self):
        """
        The camera obscura's configuration
        """
        if self._query_configuration is None:
            self._query_configuration = QueryConfiguration(self.adapter)
        return self._query_configuration
        
    @property
    def configspec_source(self):
        """
        string configuration specification
        """
        if self._configspec_source is None:
            self._configspec_source = query_configspec
        return self._configspec_source

dump_configspec = """
filename = string(default='dump.csv')
timeout = float(default=5)
"""

class DumpConfiguration(SubConfiguration):
    """
    A configuration for the dump
    """
    def __init__(self, *args, **kwargs):
        """
        DumpConfiguration constructor (allow_extras=True)
        """
        super(DumpConfiguration, self).__init__(*args, **kwargs)
        self.allow_extras = True
        return
    
    @property
    def configspec_source(self):
        """
        string configuration specification
        """
        if self._configspec_source is None:
            self._configspec_source = dump_configspec
        return self._configspec_source

node_configspec = """
username = string
password = string(default=None)
control_ip = string

# this identifies the type (only 'telnet', 'ssh', or 'fake')
connection_type = string(default='{connection_type}')

# address of the interface to test
test_ip = string

# connection time-out in seconds
timeout = float(default={timeout})

# optional prefix to add to ALL commands (default: None)
# this will be added with a space (i.e. <prefix> <command>)
# so if needed, add a semicolon like in the example between the PATH and adb

prefix = string(default=None)

# the operating system for the DUT
operating_system = string(default='{operating_system}')

# there are too many options for the different connection-types
# so you can add necessary parameters but make sure the name
# matches the parameter name
# e.g. if you need to set the port:
# port=52686
__many__ = string
""".format(connection_type=HostConstants.default_type,
           timeout=HostConstants.default_timeout,
            operating_system=HostConstants.default_operating_system)

class HostConfiguration(SubConfiguration):
    """
    A configuration for a node
    """
    @property
    def configspec_source(self):
        """
        ConfigObj-style string
        """
        if self._configspec_source is None:
            self._configspec_source = node_configspec
        return self._configspec_source

def check_direction(value):
    """
    A check-method for the configuration validation
    """
    try:
        # accept if first letter is u,d, or b
        if value[0].lower() in 'udb':
            return value
    except TypeError:
        raise VdtValueError(value)
    raise VdtValueError(value)
    return

iperf_checks.update({'check_direction': check_direction})

iperf_configspec = """
direction = check_direction(default=both)
"""
iperf_configspec += ape_iperf_configspec

class IperfPluginConfiguration(SubConfiguration):
    """
    A configuration for iperf
    """
    def __init__(self, *args, **kwargs):
        super(IperfPluginConfiguration, self).__init__(*args, **kwargs)
        self._direction = None
        self._server_settings = None
        self._client_settings = None
        self._configuration = None
        self.check_methods = iperf_checks
        self._iperf_configuration = None
        return

    @property
    def iperf_configuration(self):
        """
        The CameraObscura's IperfConfiguration
        """
        if self._iperf_configuration is None:
            self._iperf_configuration = IperfConfiguration(None)
            # set things up so it doesn't try to query Iperf_ConfigurationAdapter
            self._iperf_configuration\
                ._direction = self.direction
            self._iperf_configuration\
                ._server_settings = self.server_settings
            self._iperf_configuration\
                ._client_settings = self.client_settings
        return self._iperf_configuration

    @property
    def server_settings(self):
        """
        The IperfServerSettings
        """
        if self._server_settings is None:
            self._server_settings = IperfServerSettings()
        try:
            self._server_settings.update(self.configuration)
        except KeyError as error:
            self.logger.debug(error)            
        return self._server_settings

    @property
    def client_settings(self):
        """
        The IperfClinetSettings
        """
        if self._client_settings is None:
            self._client_settings = IperfClientSettings()
        try:
            self._client_settings.update(self.configuration)
        except KeyError as error:
            self.logger.debug(error)            
        return self._client_settings

    @property
    def direction(self):
        """
        The directions are special since they are the only things required
        
        :return: 
        """
        if self._direction is None:
            u, d, b = IperfEnum.upstream, IperfEnum.downstream, IperfEnum.both
            directions = dict(zip('u d b'.split(), (u, d, b)))

            try:
                # map only the first letter to one of the 
                direction = self.configuration[IperfEnum.direction].lower()
                self._direction = directions[direction[0]]
            except KeyError as error:
                # the validator should have grabbed a valid name
                # so this must mean there's no 'direction' option in the section
                # or no 'iperf' section
                self.logger.debug(error)
                # so use the default
                self._direction = IperfEnum.default_direction
        return self._direction
    
    @property
    def configspec_source(self):
        """
        ConfigObj-style string
        """
        if self._configspec_source is None:
            self._configspec_source = iperf_configspec
        return self._configspec_source

    def check_rep(self):
        """
        checks if the section doesn't exist first
        """
        # a hack because I didn't think about optional sections
        try:
            self.configuration
        except KeyError as error:
            self.logger.debug(error)
            self.logger.info(("section name '{0}' "
                               "not found in configuration"\
                       .format(self.section_name)))
            self.logger.info("using iperf defaults")
            return
        super(IperfPluginConfiguration, self).check_rep()
        return