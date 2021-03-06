
# python standard library
import unittest
import random

# third-party
from mock import MagicMock

# this package
from cameraobscura.attenuators.mockattenuator import MockAttenuator, LOG_STRING, MockAttenuatorConstants
from cameraobscura.tests.helpers import random_string_of_letters
from cameraobscura.attenuators.AttenuatorFactory import AttenuatorFactory


class TestMockAttenuator(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.hostname = random_string_of_letters()
        self.attenuator = MockAttenuator(self.hostname)
        self.attenuator._logger = self.logger
        return

    def test_constructor(self):
        """
        Does it even build?
        """
        self.assertEqual(self.attenuator.hostname, self.hostname)
        return

    def check_log(self, method, arguments):
        self.logger.info.assert_called_with(LOG_STRING.format(m=method,
                                                              a=arguments))
        
    def test_routes(self):
        """
        Does it log the call to routes?
        """
        expected = random.randrange(100)
        self.attenuator.routes(expected)
        self.check_log(MockAttenuatorConstants.routes, {MockAttenuatorConstants.route:expected})

        # base class doesn't use defaults, but it should
        self.attenuator.routes()
        return

    def test_getAttenuation(self):
        """
        Does it get the attenuation?
        """
        expected = random_string_of_letters()
        output = self.attenuator.getAttenuation(expected)
        self.check_log(MockAttenuatorConstants.getAttenuation,
                       {MockAttenuatorConstants.routes:expected})
        self.assertEqual(0, output)

        # check default routes set
        self.attenuator.getAttenuation()
        return

    def test_setAttenuation(self):
        """
        Does it set the attenuation?
        """
        expected_routes = random_string_of_letters()
        expected_value = random.randrange(self.attenuator.attenuation + 1, 100)
        self.assertNotEqual(expected_value, self.attenuator.getAttenuation(expected_routes))
        self.attenuator.setAttenuation(value=expected_value,
                                       routes=expected_routes)
        self.check_log(MockAttenuatorConstants.setAttenuation,
                       {MockAttenuatorConstants.value:expected_value,
                        MockAttenuatorConstants.routes:expected_routes})
        self.assertEqual(expected_value, self.attenuator.getAttenuation(expected_routes))

        self.attenuator.setAttenuation(value=expected_value)
        return

    def test_getAttenMax(self):
        """
        Does it get the max attenuation?
        """
        routes = random_string_of_letters()
        output = self.attenuator.getAttenMax(routes)
        self.check_log(MockAttenuatorConstants.getAttenMax,
                       {MockAttenuatorConstants.routes:routes})
        self.attenuator.getAttenMax()
        return

    def test_factory(self):
        """
        Does the factory build it correctly?
        """
        attenuator = AttenuatorFactory.GetAttenuator(self.attenuator.__class__.__name__,
                                                     self.hostname)
        self.assertEqual(self.hostname, attenuator.hostname)
        return
        
# end class TestMockAttenuator    
