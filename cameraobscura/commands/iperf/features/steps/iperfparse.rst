IperfParse Feature
==================

.. literalinclude:: ../iperfparse.feature
   :language: gherkin




Scenario: The default IperfParser is used
-----------------------------------------


.. code:: python

    @given("no parser")
    def no_parser(context):
        client_settings = MagicMock()
        context.iperf = Iperf(None,
                              None,
                              server_settings=None,
                              client_settings=client_settings)
        return




.. code:: python

    @when("the Iperf.parser is checked")
    def check_parser(context):
        context.parser = context.iperf.parser
        return




.. code:: python

    @then("it is the IperfParser")
    def assert_iperf_parser(context):
        assert_that(context.parser,
                    is_(instance_of(IperfParser)))    
        return



Scenario: IperfParser parses outcome
------------------------------------


.. code:: python

    @given("An Iperf instance")
    def iperf_run_instance(context):
        context.client_settings = MagicMock()
        context.parser = MagicMock()
        context.fake_output = 'a b c d e'.split()
        context.parser.bandwidths = numpy.random.random_sample(5)
        context.expected = [call(output) for output in context.fake_output]
    
        mock_definition = MagicMock(name='IperfParser Definition')
        mock_definition.return_value = context.parser
        mock_file = mock_open()
        mock_os = MagicMock()
    
        names = '__builtin__.open os.makedirs iperflexer.iperfparser.IperfParser'.split()
        mocks = (mock_file, mock_os, mock_definition)
        context.patches = [patch(name, mocks[index]) for index, name in enumerate(names)]
    
        context.iperf = Iperf(None, None,
                              server_settings=None,
                              client_settings=context.client_settings,
                              parser=context.parser)
    
        context.host = MagicMock()
        context.host.exec_command.return_value = (None,
                                          context.fake_output,
                                          '')
    
        return




.. code:: python

    @when("the ``run`` method is called")
    def call_run(context):
        settings = IperfSettings.IperfClientSettings(server='fake')
    
        with nested(*context.patches):
            context.iperf.run(host=context.host,
                              settings=settings,
                              filename='apple')
        return




.. code:: python

    @then("the output is given to the IperfParser")
    def check_output(context):
        assert_that(context.parser.mock_calls,
                    contains(*context.expected))
        return



Scenario: IperfParser sets client for client
--------------------------------------------

Example: client
~~~~~~~~~~~~~~~


.. code:: python

    @given("an Iperf instance with fake parser")
    def fake_parser(context):
        context.parser = MagicMock()
        context.parser.bandwidths =  numpy.random.random_sample(5)
        context.fake_output = 'a b c d e'.split()
        context.summary = numpy.mean(context.parser.bandwidths)    
    
        mock_definition = MagicMock(name='IperfParser Definition')
        mock_definition.return_value = context.parser
        mock_file = mock_open()
        mock_os = MagicMock()
    
        names = '__builtin__.open os.makedirs iperflexer.iperfparser.IperfParser'.split()
        mocks = (mock_file, mock_os, mock_definition)
        context.patches = [patch(name, mocks[index]) for index, name in enumerate(names)]
    
        context.iperf = Iperf(None,
                              None,
                              client_settings=MagicMock(),
                              server_settings=None,
                              parser=context.parser)
        context.host = MagicMock()
        context.host.exec_command.return_value = (None,
                                          context.fake_output,
                                          '')
        return




.. code:: python

    @when("the ``run`` method is called and the client summary checked")
    def check_client_outcome(context):
        settings = IperfSettings.IperfClientSettings(server='fake')
        with nested(*context.patches):
            context.iperf.run(host=context.host,
                              settings=settings,
                              filename='apple')
    
        context.client_summary = context.iperf.client_summary
        return




.. code:: python

    @then("the summary of client values is set")
    def assert_client_summary(context):
        assert_that(context.client_summary,
                    is_(equal_to(context.summary)))
        return



Example: server
~~~~~~~~~~~~~~~


.. code:: python

    @when("the ``run`` method is called and the server summary checked")
    def check_server_outcome(context):    
        settings = IperfSettings.IperfServerSettings()
            
        with nested(*context.patches):
            #with patch('iperflexer.iperfparser.IperfParser', mock_definition):
            context.iperf.run(host=context.host,
                              settings=settings,
                              filename='apple')
        context.server_summary = context.iperf.server_summary
        return




.. code:: python

    @then("the summary of server values is set")
    def assert_server_summary(context):
        print(context.iperf.parser.bandwidths)
        assert_that(context.summary,
                    is_(equal_to(context.server_summary)))
        return



Scenario: Iperf Settings are unknown
------------------------------------

Given an Iperf instance with fake parser


.. code:: python

    @when("the ``run`` method is called with unknown settings type")
    def unknown_settings(context):
        return




.. code:: python

    @then('a CameraObscura error is raised')
    def raise_error(context):
        mock_file = mock_open()
        with patch('__builtin__.open', mock_file):
            with patch('os.makedirs', create=True):
                assert_that(calling(context.iperf.run).with_args(host=context.host,
                                                         settings=MagicMock(),
                                                         filename='asoethu'),
                                                         raises(CameraobscuraError))
        return


