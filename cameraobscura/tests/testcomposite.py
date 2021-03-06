
# python standard library
import unittest
import random

# third-party
from mock import Mock, call

# this package
from cameraobscura.utilities.composite import TheComposite


class TestComposite(unittest.TestCase):
    def setUp(self):
        self.components = [Mock() for component in xrange(random.randrange(1, 100))]
        self.composite = TheComposite(components=self.components)
        return

    def test_constructor(self):
        """
        Does it build correctly?
        """
        self.assertEqual(self.components, self.composite.components)
        return

    def test_call(self):
        """
        Does it call all the components?
        """
        logger = Mock()
        self.composite._logger = logger
        self.composite()
        calls = [call("Calling Component: {0}".format(component)) for component in self.components]
        self.assertEqual(logger.info.mock_calls, calls)        
        for component in self.components:
            component.assert_called_with()
            
        return
# end class TestComposite    
