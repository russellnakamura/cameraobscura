
# python standard library
import unittest
import random

# this package
from cameraobscura import CameraobscuraError
from cameraobscura.commands.iperf.IperfSettings import IperfClientSettings 
from cameraobscura.commands.iperf.IperfSettings import IperfClientConstants
from cameraobscura.tests.helpers import random_string_of_letters


SERVER_ADDRESS = random_string_of_letters(10)

client_settings = {'bandwidth': random.randrange(100),
                   'dualtest':True,
                   'tradeoff': True,
                   'time': random.randrange(100),
                   'fileinput': random_string_of_letters(10),
                   'stdin': True,
                   'listenport':random.randrange(2000, 5000),
                   'parallel': random.randrange(100),
                   'ttl':random.randrange(100)}

class TestIperfClientSettings(unittest.TestCase):
    def setUp(self):
        self.server = SERVER_ADDRESS
        self.configuration = IperfClientSettings(server=self.server)
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        # needs a server hostname
        with self.assertRaises(CameraobscuraError):
            configuration = IperfClientSettings()
            # if no server is set should raise an error
            configuration.prefix
        self.assertEqual(" --client " + self.server, self.configuration.prefix)

        self.assertEqual(' --client {0}'.format(self.server),
                         str(self.configuration))
        return

    def test_bandwidth(self):
        """
        Does it set the UDP bandwidth?
        """
        # integer
        value = client_settings['bandwidth']
        self.configuration.bandwidth = value
        self.assertEqual(" --client {0} --bandwidth {1}".format(self.server,
                                                                value), str(self.configuration))

        # string
        value = "{0}{1}".format(value,
                                random.choice('KM'))
        self.configuration.bandwidth = value
        self.assertEqual(self.configuration.prefix + " --bandwidth {0}".format(value),
                         str(self.configuration))

        # bad value
        value = random_string_of_letters()
        with self.assertRaises(CameraobscuraError):            
            self.configuration.bandwidth = value
        return

    def test_dualtest(self):
        """
        Does it set the bi-directional test flag?
        """
        self.configuration.dualtest = True
        self.assertEqual(self.configuration.prefix + " --dualtest ", str(self.configuration))
        return

    def test_num(self):
        """
        Does it set the flag for the number of bytes to send?
        """
        # integer
        value = random.randrange(200)
        self.configuration.num = value
        self.assertEqual(self.configuration.prefix + " --num {0}".format(value),
                         str(self.configuration))

        # string
        value = "{0}{1}".format(value, random.choice("KM"))
        self.configuration.num = value
        self.assertEqual(self.configuration.prefix + " --num {0}".format(value),
                         str(self.configuration))
        # bad string
        with self.assertRaises(CameraobscuraError):
            self.configuration.num = random_string_of_letters()
        return

    def test_tradeoff(self):
        """
        Does it set the flag to do a bi-directional test separately?
        """
        self.configuration.tradeoff = True
        self.assertEqual(self.configuration.prefix + ' --tradeoff ', str(self.configuration))

        # turn it off
        self.configuration.tradeoff = False
        self.assertEqual(self.configuration.prefix, str(self.configuration))
        return

    def test_time(self):
        """
        Does it set the length of time (in seconds) to transmit?
        """
        # negative numbers are allowed by iperf (infinite time)
        value = random.randrange(-1000, 1000)
        self.configuration.time = value
        self.assertEqual(self.configuration.prefix + " --time {0}".format(value),
                         str(self.configuration))
        return

    def test_fileinput(self):
        """
        Does it set a file name to provide data to transmit?
        """
        value = random_string_of_letters()
        self.configuration.fileinput = value
        self.assertEqual(self.configuration.prefix + " --fileinput {0}".format(value),
                         str(self.configuration))
        return

    def test_stdin(self):
        """
        Does it set the flag to take data from stdin?
        """
        self.configuration.stdin = True
        self.assertEqual(self.configuration.prefix + ' --stdin ',
                         str(self.configuration))
        return

    def test_listenport(self):
        """
        Does it set the port to listen to for bi-directional testing?
        """
        value = random.randrange(2000, 5000)
        self.configuration.listenport = value
        self.assertEqual(self.configuration.prefix + ' --listenport {0}'.format(value),
                         str(self.configuration))

        # bad value
        with self.assertRaises(CameraobscuraError):
            self.configuration.listenport = random.randrange(-100, 1024)
        return

    def test_parallel(self):
        """
        Does it set the number of threads to run?
        """
        value = random.randrange(100)
        self.configuration.parallel = value
        self.assertEqual(self.configuration.prefix + " --parallel {0}".format(value),
                         str(self.configuration))
        return

    def test_ttl(self):
        """
        Does it set the time-to-live for multicast traffic?
        """
        value = random.randrange(100)
        self.configuration.ttl = value
        self.assertEqual(self.configuration.prefix + " --ttl {0}".format(value),
                         str(self.configuration))
        return

    def test_linux_congestion(self):
        """
        Does it set the (Linux) TCP congestion control algorithm?
        """
        value = random_string_of_letters()
        self.configuration.linux_congestion = value
        self.assertEqual(self.configuration.prefix + ' --linux-congestion {0}'.format(value),
                         str(self.configuration))
        return

    def test_whole_shebang(self):
        """
        Does it correctly work with random settings?
        """
        # pick a sub-set of keys
        parameters = random.sample(client_settings.keys(),
                                   random.randrange(len(client_settings)))

        # put them in the same order as the IperfClient expects
        parameters = [parameter for parameter in IperfClientConstants.options
                      if parameter in parameters]
        # set the values
        for parameter in parameters:
            setattr(self.configuration, parameter, client_settings[parameter])

        # change the booleans to empty strings
        output = client_settings.copy()
        for key in output:
            if output[key] is True:
                output[key] = ''
        expected = self.configuration.prefix + "".join([" --{0} {1}".format(parameter, output[parameter]) for parameter in parameters])
        self.assertEqual(expected, str(self.configuration))
        return

    def test_new_hostname(self):
        """
        Does it let you change the server hostname while preserving the other settings?
        """
        new_hostname = random_string_of_letters(10)
        self.configuration.server = new_hostname

        # pick a sub-set of keys
        parameters = random.sample(client_settings.keys(),
                                   random.randrange(len(client_settings)))

        # put them in the same order as the IperfClient expects
        parameters = [parameter for parameter in IperfClientConstants.options
                      if parameter in parameters]
        # set the values
        for parameter in parameters:
            setattr(self.configuration, parameter, client_settings[parameter])

        # change the booleans to empty strings
        output = client_settings.copy()
        for key in output:
            if output[key] is True:
                output[key] = ''
        expected = (" --client {0}".format(new_hostname) +
                    "".join([" --{0} {1}".format(parameter, output[parameter]) for parameter in parameters]))
        self.assertEqual(expected, str(self.configuration))
        return

    def test_update(self):
        """
        Does it update from a dictionary?
        """
        client_settings = {'time':500, 'parallel':5}
        general_settings = {'format':'b', 'interval':12}

        keys = client_settings.keys() + general_settings.keys()
        values = client_settings.values() + general_settings.values()
        settings = dict(zip(keys, values))
        self.configuration.update(settings)

        for parameter, value in settings.iteritems():
            self.assertEqual(self.configuration.get(parameter), value)            
        return
