
# python standard library
import logging

# this package
from cameraobscura.commands.ping.ping import Ping

class PingBuilder(object):
    """
    A builder of pings
    """
    def __init__(self, connection, configuration):
        """
        PingBuilder Constructor

        :param:

         - `connection`: connection to the device that will send pings
         - `configuration`: a PingConfiguration
        """
        super(PingBuilder, self).__init__()
        self._logger = None
        self.connection = connection
        self.configuration = configuration
        self._product = None
        return

    @property
    def logger(self):
        """
        :return: A logging object.
        """
        if self._logger is None:
            self._logger = logging.getLogger("{0}.{1}".format(self.__module__,
                                  self.__class__.__name__))
        return self._logger

    @property
    def product(self):
        """
        A built Ping instance
        """
        if self._product is None:
            self.logger.debug("Building the ping with '{0}' and '{1}'".format(self.connection,
                                                                              self.configuration))
            self._product = Ping(connection=self.connection,
                                 target=self.configuration.target,
                                 time_limit=self.configuration.time_limit,
                                 timeout=self.configuration.timeout,
                                 threshold=self.configuration.threshold,
                                 operating_system=self.configuration.operating_system,
                                 arguments=self.configuration.arguments,
                                 data_expression=self.configuration.data_expression,
                                 trap_errors=self.configuration.trap_errors)
        return self._product
# end class PingBuilder