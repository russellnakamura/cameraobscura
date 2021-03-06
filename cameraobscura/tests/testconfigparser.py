
SECTION = 'BunnyGrahams'
SAMPLE = """
[{0}]
calories = 120
fat = 4
protein = 2
bunnies = Ted
furry = False
""".format(SECTION)
DEFAULTS = {'calories':120,
            'healthy':'False',
            'sugar': '999',
            'cow': "Annabelle"}


# python standard library
import unittest
import ConfigParser
import io



class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser.SafeConfigParser(defaults=DEFAULTS)
        self.parser.readfp(io.BytesIO(SAMPLE))
        return

    def test_defaults(self):
        """
        Does it substitute defaults passed in on creation?
        """
        # passing in an int as a default works
        self.assertEqual(DEFAULTS['calories'], self.parser.getint('BunnyGrahams',
                                                                  'calories'))

        # so it might be safer to only pass in strings (see the Boolean test)
        self.assertEqual(999, self.parser.getint(SECTION, 'sugar'))
        
        # passing in a Boolean won't (it's using string coercion)
        self.assertEqual(False, self.parser.getboolean(SECTION,
                                                       'healthy'))
        self.assertEqual(DEFAULTS['cow'], self.parser.get(SECTION,
                                                          'cow'))                                                                  
        return

    def test_no_default(self):
        """
        Does it raise a NoOptionError?
        """
        with self.assertRaises(ConfigParser.NoOptionError):
            self.parser.get(SECTION, 'apple')
        return

    def test_vars(self):
        """
        Do the getters accept default values?
        """
        OPTION, VALUE = 'ape', 'man'
        default = {OPTION : VALUE}
        with self.assertRaises(ConfigParser.NoOptionError):
            self.parser.get(SECTION, OPTION)
        self.assertEqual(VALUE, self.parser.get(SECTION, OPTION, vars=default))

        OPTION, VALUE = 'age', '2'
        default = {OPTION:VALUE}
        with self.assertRaises(ConfigParser.NoOptionError):
            self.parser.getint(SECTION, OPTION)
        return

    def test_int_vars(self):
        """
        Well, this turns out not to work as expected -- getint doesn't accept vars.
        """
        OPTION, VALUE = 'age', '2'
        default = {OPTION:VALUE}
        with self.assertRaises(ConfigParser.NoOptionError):
            self.parser.getint(SECTION, OPTION)
        with self.assertRaises(TypeError):
            self.parser.getint(SECTION, OPTION, vars=default)
        self.assertEqual(2, int(self.parser.get(SECTION, OPTION, vars=default)))
        return

    def test_bool_vars(self):
        """
        As with getint, getboolean turns out not to accept defaults.
        """
        OPTION, VALUE = 'truth', 'false'
        default = {OPTION: VALUE}
        with self.assertRaises(TypeError):
            self.parser.getboolean(SECTION, OPTION, vars=default)

        # but if you expect it to be persistent, you can add it to the defaults?
        with self.assertRaises(ConfigParser.NoOptionError):
            self.parser.getint(SECTION, OPTION)

        # the defaults dict is private, you could probably also use _defaults instead of the getter
        self.parser.defaults()[OPTION] = VALUE
        self.assertFalse(self.parser.getboolean(SECTION,
                                                OPTION))

        # This now means that all sections will have this as a default so it's not the same as using 'vars'
        del(self.parser.defaults()[OPTION])
        with self.assertRaises(ConfigParser.NoOptionError):
            self.parser.getboolean(SECTION, OPTION)
            
        return
        
