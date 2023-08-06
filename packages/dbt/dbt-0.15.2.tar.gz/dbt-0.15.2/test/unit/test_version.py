import unittest
from unittest.mock import patch, MagicMock

import dbt.main
import dbt.version
import sys


class VersionTest(unittest.TestCase):

    @patch("dbt.version.__version__", "0.10.0")
    @patch('dbt.version.requests.get')
    def test_versions_equal(self, mock_get):
        mock_get.return_value.json.return_value = {'info': {'version': '0.10.0'}}

        latest_version = dbt.version.get_latest_version()
        installed_version = dbt.version.get_installed_version()
        version_information = dbt.version.get_version_information()

        expected_version_information = "installed version: 0.10.0\n" \
            "   latest version: 0.10.0\n\n" \
            "Up to date!"

        self.assertEqual(latest_version, installed_version)
        self.assertEqual(latest_version, installed_version)
        self.assertMultiLineEqual(version_information,
                                  expected_version_information)

    @patch("dbt.version.__version__", "0.10.2-a1")
    @patch('dbt.version.requests.get')
    def test_installed_version_greater(self, mock_get):
        mock_get.return_value.json.return_value = {'info': {'version': '0.10.1'}}

        latest_version = dbt.version.get_latest_version()
        installed_version = dbt.version.get_installed_version()
        version_information = dbt.version.get_version_information()

        expected_version_information = "installed version: 0.10.2-a1\n" \
            "   latest version: 0.10.1\n\n" \
            "Your version of dbt is ahead of the latest release!"

        assert installed_version > latest_version
        self.assertMultiLineEqual(version_information,
                                  expected_version_information)

    @patch("dbt.version.__version__", "0.9.5")
    @patch('dbt.version.requests.get')
    def test_installed_version_lower(self, mock_get):
        mock_get.return_value.json.return_value = {'info': {'version': '0.10.0'}}

        latest_version = dbt.version.get_latest_version()
        installed_version = dbt.version.get_installed_version()
        version_information = dbt.version.get_version_information()

        expected_version_information = "installed version: 0.9.5\n" \
            "   latest version: 0.10.0\n\n" \
            "Your version of dbt is out of date! " \
            "You can find instructions for upgrading here:\n" \
            "https://docs.getdbt.com/docs/installation"

        assert installed_version < latest_version
        self.assertMultiLineEqual(version_information,
                                  expected_version_information)

    # suppress having version info printed to the screen during tests.
    @patch('sys.stderr')
    @patch('dbt.version.requests.get')
    def test_dbt_version_flag(self, mock_get, stderr):
        mock_get.return_value.json.return_value = {'info': {'version': '0.10.1'}}

        with self.assertRaises(SystemExit) as exc:
            dbt.main.handle_and_check(['--version'])
        self.assertEqual(exc.exception.code, 0)
