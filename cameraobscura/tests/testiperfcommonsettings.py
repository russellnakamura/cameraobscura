
# python standard library
import unittest
import random
import string

# this package
from cameraobscura import CameraobscuraError
from cameraobscura.commands.iperf.IperfSettings import IperfGeneralSettings
from cameraobscura.commands.iperf.IperfSettings import IperfConstants
from cameraobscura.tests.helpers import random_string_of_letters


TRUE_OR_FALSE = (True, False)
common_settings = {'format': random.choice('bkmKM'),
                   'interval': random.randrange(1, 100),
                   'len': random.choice((random.randrange(2000),
                                        "{0}{1}".format(random.randrange(2000),
                                          random.choice('KM ')))),
                    'print_mss': True,
                    'output': random_string_of_letters(),
                    'port': random.randrange(2000, 10000),
                    'window': "{0}{1}".format(random.randrange(2000), random.choice('KM')),
                    'compatibility': True,
                    'mss': random.randrange(5000),
                    'nodelay': True,
                    'version': True,
                    'IPv6Version':True,
                    "reportexclude": random.choice('CDMSV'),
                    'reportstyle':random.choice('cC')}
class TestIperfGeneralSettings(unittest.TestCase):
    def setUp(self):        
        self.settings = IperfGeneralSettings()
        return
        
    def test_constructor(self):
        """
        Does it build correctly?
        """
        return

    def test_format(self):
        """
        Does it set the format correctly?
        """
        # check default
        self.assertIsNone(self.settings.format)
        self.assertEqual('', str(self.settings))

        # set to valid format
        self.settings.format = 'K'
        self.assertEqual('K', self.settings.format)
        self.assertEqual(" --format K", str(self.settings))

        # set to invalid format
        with self.assertRaises(CameraobscuraError):
            self.settings.format = 'v'
        return

    def test_interval(self):
        """
        Does it check and set the reporting interval correctly?
        """
        # default
        self.assertIsNone(self.settings.interval)

        # valid
        value = random.randrange(100)
        self.settings.interval = value
        self.assertAlmostEqual(self.settings.interval, value)
        self.assertEqual(" --interval {0}".format(value), str(self.settings))

        # invalid
        value = -1 * random.randrange(1, 100)
        with self.assertRaises(CameraobscuraError):
            self.settings.interval = value
        return

    def test_len(self):
        """
        Does it set the length of the read/write buffer?
        """
        # default
        self.assertIsNone(self.settings.len)

        # set to value
        value = random.randrange(100)
        caster = random.choice((int, float))
        value = caster(value)
        self.settings.len = value
        self.assertEqual(" --len {0}".format(value), str(self.settings))

        # bad-value
        # iperf appears to not be case-sensitive for this value
        # and it just ignores nonsense characters (but we won't)
        source = string.ascii_lowercase[:]
        source = source.replace("k", '')
        source = source.replace("m", '')
        value = "{v}{s}".format(v=value, s=random.choice(source))
        with self.assertRaises(CameraobscuraError, msg="Didn't raise error with value: {0}".format(value)):
            self.settings.len = value
        return

    def test_print_mss(self):
        """
        Does it set the option to print the TCP maximum segment size?
        """
        # default
        self.assertIsNone(self.settings.print_mss)

        # make it print
        self.settings.print_mss = True
        self.assertEqual(' --print_mss ', str(self.settings))

        # now turn it off
        self.settings.print_mss = 0
        self.assertIsNone(self.settings.print_mss)
        return

    def test_output(self):
        """
        Does it designate an output file name?
        """
        #default
        self.assertIsNone(self.settings.output)

        # set filename
        value = random_string_of_letters()
        self.settings.output = value
        self.assertEqual(" --output {0}".format(value), str(self.settings))

        # bad filename
        value = random_string_of_letters() + ' ' + random_string_of_letters()
        with self.assertRaises(CameraobscuraError):
            self.settings.output = value
        return

    def test_port(self):
        """
        Does it set the port?
        """
        # default
        self.assertIsNone(self.settings.port)

        # set the port
        value = random.randrange(1024, 9999)
        self.settings.port = value
        self.assertEqual(" --port {0}".format(value), str(self.settings))

        # bad port
        value = random_string_of_letters()
        with self.assertRaises(CameraobscuraError):
            self.settings.port = value

        # bad port 2
        value = random.randrange(1024)
        with self.assertRaises(CameraobscuraError):
            self.settings.port = value
        return

    def test_window(self):
        """
        Does it set the TCP window size?        
        """
        # default
        self.assertIsNone(self.settings.window)

        # set the window to a number
        caster = random.choice((int, float))
        value = random.choice((-1, 1)) * caster(random.randrange(100))
        self.settings.window = value
        self.assertEqual(" --window {0}".format(value),
                         str(self.settings))

        # give units
        unit = random.choice('KM')
        value = '{0}{1}'.format(value, unit)

        # bad value
        value = random_string_of_letters()
        with self.assertRaises(CameraobscuraError):
            self.settings.window = value

        return

    def test_compatibility(self):
        """
        Does it set the compatibility flag?
        """
        # default
        self.assertIsNone(self.settings.compatibility)

        # set it
        self.settings.compatibility = True
        print self.settings.compatibility

        self.assertEqual(' --compatibility ', str(self.settings))        
        return

    def test_mss(self):
        """
        Does it set the TCP maximum segment size?
        """
        # default
        self.assertIsNone(self.settings.mss)

        # set to a number
        value = random.randrange(100)
        self.settings.mss = value
        self.assertEqual(" --mss {0}".format(value), str(self.settings))

        #invalid setting
        value = random_string_of_letters()
        with self.assertRaises(CameraobscuraError):
            self.settings.mss = value
        return

    def test_nodelay(self):
        """
        Does it set the nodelay flag?
        """
        # default
        self.assertIsNone(self.settings.nodelay)

        # turn it on
        self.settings.nodelay = True
        self.assertEqual(' --nodelay ', str(self.settings))
        return

    def test_version(self):
        """
        Does it set the version flag?
        """
        # default
        self.assertIsNone(self.settings.version)

        # turn it on
        self.settings.version = True
        self.assertEqual(" --version ", str(self.settings))
        return

    def test_IPv6Version(self):
        """
        Does it set the IP v6 flag?
        """
        # default
        self.assertIsNone(self.settings.IPv6Version)

        # turn it on
        self.settings.IPv6Version = random.choice((1, True, 'a'))
        self.assertEqual(' --IPv6Version ', str(self.settings))
        return

    def test_reportexclude(self):
        """
        Does it set the flag to turn of some reporting?
        """
        # default
        self.assertIsNone(self.settings.reportexclude)

        # turn things off
        options = random.randrange(1, 4)
        value = ''.join([random.choice('CDMSV') for option in xrange(options)])
        self.settings.reportexclude = value
        self.assertEqual(' --reportexclude {0}'.format(value), str(self.settings))

        # bad exclusion (number)
        with self.assertRaises(CameraobscuraError):
            self.settings.reportexclude = random.randrange(100)

        # invalid option
        with self.assertRaises(CameraobscuraError):
            self.settings.reportexclude = random.choice('ABEFGHIJKLNOP')
        return

    def test_reportstyle(self):
        """
        Does it change the output to csv-format?
        """
        # default
        self.assertIsNone(self.settings.reportstyle)

        # set it to CSV
        value = random.choice('cC')
        self.settings.reportstyle = value
        self.assertEqual(' --reportstyle {0}'.format(value), str(self.settings))

        # set it to a bad value
        with self.assertRaises(CameraobscuraError):
            self.settings.reportstyle = random.randrange(100)
        with self.assertRaises(CameraobscuraError):
            source = string.ascii_lowercase[:]
            source = source.replace('c', '')           
            self.settings.reportstyle = random.choice(source)
        return

    def test_update(self):
        """
        Does it setup the settings from a dictionary?
        """
        self.assertEqual("", str(self.settings))

        # the combination explosion has set in, this won't be exhaustive
        # add to it as the case arises
        extra_parameter = random_string_of_letters()
        extra_value = random.randrange(999)
        parameters = {'format': random.choice('bkmKM'),
                      'interval': random.randrange(100),
                      'len': '{0}K'.format(random.randrange(100)),
                      'window': random.randrange(2000)}

        copy = dict(parameters.items())

        parameters[extra_parameter] = extra_value
        
        leftovers = self.settings.update(parameters)        
        self.assertDictEqual({extra_parameter:extra_value},
                             leftovers)

        for key, item in copy.iteritems():
            self.assertEqual(item, getattr(self.settings, key))
        return

    def test_string(self):
        """
        Does it create the string like we expect?
        """
        samples = random.sample(common_settings.keys(),
                               random.randrange(len(common_settings)))
        settings = dict(zip(samples, (common_settings[sample] for sample in samples)))
        configuration = IperfGeneralSettings(**settings)
        # put it in order
        samples = [sample for sample in IperfConstants.general_options if sample in samples]

        # change booleans to empty strings        
        for setting, value in common_settings.iteritems():
            if value in TRUE_OR_FALSE:
                common_settings[setting] = ""
        expected = "".join((" --{0} {1}".format(sample, common_settings[sample]) for sample in samples))
        self.assertEqual(expected, str(configuration))
# end TestIperfGeneralSettings    
