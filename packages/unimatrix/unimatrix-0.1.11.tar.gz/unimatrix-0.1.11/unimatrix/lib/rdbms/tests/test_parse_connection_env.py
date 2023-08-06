import unittest

from ..config import parse_environment


class ParseEnvironmentTestCase(unittest.TestCase):

    def test_unsupported_engine_raises_valueerror(self):
        env = {
            'DB_ENGINE': 'foo',
        }
        with self.assertRaises(ValueError):
            opts = parse_environment(env)

    def test_empty_environment_returns_none(self):
        opts = parse_environment({})
        self.assertEqual(opts, None)

    def test_parse_postgresql_with_defaults(self):
        env = {
            'DB_ENGINE': 'postgresql',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, 'localhost')
        self.assertEqual(opts.port, 5432)
        self.assertEqual(opts.name, None)
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)

    def test_parse_mysql_with_defaults(self):
        env = {
            'DB_ENGINE': 'mysql',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, 'localhost')
        self.assertEqual(opts.port, 3306)
        self.assertEqual(opts.name, None)
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)

    def test_parse_sqlite_with_defaults(self):
        env = {
            'DB_ENGINE': 'sqlite',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, None)
        self.assertEqual(opts.port, None)
        self.assertEqual(opts.name, ":memory:")
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)
