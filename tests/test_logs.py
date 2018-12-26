from unittest import TestCase
from unittest.mock import patch

from log_tools import logs


class TestLogs(TestCase):
    def setUp(self):
        pass

    def test_parser_legacy_app(self):
        with patch('sys.argv', ['', 'services']):
            parser = logs.get_parser()
            args = vars(parser.parse_args())
            self.assertEqual('services', args['app'])
            self.assertEqual(False, args['show_apps'])
            self.assertEqual(False, args['client_int'])
            self.assertEqual(False, args['int'])
            self.assertEqual(False, args['quality'])

    def test_parser_completion(self):
        with patch('sys.argv', ['', '-j']):
            parser = logs.get_parser()
            args = vars(parser.parse_args())
            self.assertEqual(None, args['app'])
            self.assertEqual(True, args['show_apps'])
            self.assertEqual(False, args['client_int'])
            self.assertEqual(False, args['int'])
            self.assertEqual(False, args['quality'])

    def test_parser_int_app(self):
        with patch('sys.argv', ['', '--int', 'client']):
            parser = logs.get_parser()
            args = vars(parser.parse_args())
            self.assertEqual('client', args['app'])
            self.assertEqual(False, args['show_apps'])
            self.assertEqual(False, args['client_int'])
            self.assertEqual(True, args['int'])
            self.assertEqual(False, args['quality'])

    @patch('sys.argv', ['', 'unknown'])
    @patch('log_tools.logs.argparse.ArgumentParser.print_help')
    def test_cli_print_help(self, mock_print_help):
        logs.command_line_runner()
        mock_print_help.assert_called_once()

    @patch('sys.argv', ['', 'services'])
    @patch('log_tools.log.LegacyLog.tail')
    def test_cli_services(self, mock_legacy_logs):
        logs.command_line_runner()
        mock_legacy_logs.assert_called_once_with(None)

    @patch('sys.argv', ['', '-q', 'playout'])
    @patch('log_tools.log.LegacyLog.tail')
    def test_cli_quality(self, mock_legacy_logs):
        logs.command_line_runner()
        mock_legacy_logs.assert_called_once_with('quality')

    @patch('sys.argv', ['', '-i', 'my'])
    @patch('log_tools.log.LegacyLog.tail')
    def test_cli_int(self, mock_legacy_logs):
        logs.command_line_runner()
        mock_legacy_logs.assert_called_once_with('int')

    @patch('sys.argv', ['', 'partner-accounts'])
    @patch('log_tools.log.KubernetesLog.tail')
    def test_cli_default_kube(self, mock_kubernetes_logs):
        logs.command_line_runner()
        mock_kubernetes_logs.assert_called_once_with(None)

    @patch('sys.argv', ['', '--int', 'pa'])
    @patch('log_tools.log.KubernetesLog.tail')
    def test_cli_int_kube(self, mock_kubernetes_logs):
        logs.command_line_runner()
        mock_kubernetes_logs.assert_called_once()
        mock_kubernetes_logs.assert_called_once_with('int')
