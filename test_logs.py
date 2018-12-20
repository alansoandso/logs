from unittest import TestCase, mock
from unittest.mock import patch
import logs


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

    def test_parser_int_app(self):
        with patch('sys.argv', ['', '--int', 'client']):
            parser = logs.get_parser()
            args = vars(parser.parse_args())
            self.assertEqual('client', args['app'])
            self.assertEqual(False, args['show_apps'])
            self.assertEqual(False, args['client_int'])
            self.assertEqual(True, args['int'])
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

    @patch('sys.argv', ['', 'unknown'])
    @patch('logs.argparse.ArgumentParser.print_help')
    def test_cli_unknown_app(self, mock_print_help):
        logs.command_line_runner()
        mock_print_help.assert_called_once()

    @patch('logs.kubernetes_logs')
    def test_kubernetes_route(self, mock_kubernetes_logs):
        logs.partner_logs({'kubernetes': {}}, 'quality')
        mock_kubernetes_logs.assert_called_once()

    @patch('sys.argv', ['', 'services'])
    @patch('logs.legacy_logs')
    def test_cli_services(self, mock_legacy_logs):
        logs.command_line_runner()
        mock_legacy_logs.assert_called_with({'name': 'services', 'env': 'quality', 'jq': True}, None)

    @patch('sys.argv', ['', '-i', 'my'])
    @patch('logs.legacy_logs')
    def test_cli_int_alt_my(self, mock_legacy_logs):
        logs.command_line_runner()
        mock_legacy_logs.assert_called_with({'name': 'personalisation', 'env': 'quality', 'jq': True}, 'int')

    @patch('sys.argv', ['', '-q', 'my'])
    @patch('logs.legacy_logs')
    def test_cli_qa_my(self, mock_legacy_logs):
        logs.command_line_runner()
        mock_legacy_logs.assert_called_with({'name': 'personalisation', 'env': 'quality', 'jq': True}, 'quality')

    @patch('sys.argv', ['', 'partner-accounts'])
    @patch('logs.kubernetes_logs')
    def test_cli_default_kube(self, mock_kubernetes_logs):
        logs.command_line_runner()
        mock_kubernetes_logs.assert_called_with({'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'env': 'int', 'app': 'partner-accounts-service'}, None)

    @patch('sys.argv', ['', 'pa'])
    @patch('logs.kubernetes_logs')
    def test_cli_default_kube(self, mock_kubernetes_logs):
        logs.command_line_runner()
        mock_kubernetes_logs.assert_called_with({'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'env': 'int', 'app': 'partner-accounts-service'}, None)

    @patch('logs.check_output')
    @patch('logs.os')
    def test_kubernetes_logs_client_int(self, mock_os, mock_check_output):
        mock_check_output.return_value = """
        NAME                                        READY     STATUS    RESTARTS   AGE
        partner-accounts-service-me-me-me           1/1       Running   0          2h
        partner-accounts-service-75f66cc6f6-sw62w   1/1       Running   0          2h
        """
        logs.kubernetes_logs({'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'env': 'int', 'app': 'partner-accounts-service'}, None)
        mock_check_output.assert_called_with(['kubectl', '--context=dev.cosmic.sky', '-n', 'partner-accounts-int', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=dev.cosmic.sky -n partner-accounts-int logs -f partner-accounts-service-me-me-me ')

    @patch('sys.argv', ['', 'mytv'])
    @patch('logs.kubernetes_logs')
    def test_cli_default_mytv(self, mock_kubernetes_logs):
        logs.command_line_runner()
        mock_kubernetes_logs.assert_called_with({'context': 'development', 'namespace': 'platform', 'env': None, 'app': 'mytv-e05', 'jq': True}, None)

    @patch('logs.check_output')
    @patch('logs.os')
    def test_kubernetes_logs_mytv_logs(self, mock_os, mock_check_output):
        mock_check_output.return_value = """
        NAME                                READY     STATUS    RESTARTS   AGE
        mytv-e05-pickme                     1/1       Running   0          35d
        prometheus-stack-3169584513-0jk3j   2/2       Running   0          103d
        """
        logs.kubernetes_logs({'context': 'development', 'namespace': 'platform', 'env': None, 'app': 'mytv-e05', 'jq': True}, None)
        mock_check_output.assert_called_with(['kubectl', '--context=development', '-n', 'platform', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=development -n platform logs -f mytv-e05-pickme  | jq')

    @patch('sys.argv', ['--quality', 'mytv'])
    @patch('logs.kubernetes_logs')
    def test_cli_qa_mytv(self, mock_kubernetes_logs):
        logs.command_line_runner()
        mock_kubernetes_logs.assert_called_with({'context': 'development', 'namespace': 'platform', 'env': None, 'app': 'mytv-e05', 'jq': True}, None)

    @patch('sys.argv', ['', '-i', 'mytv'])
    @patch('logs.check_output')
    @patch('logs.os.system')
    def test_cli_qa_mytv_logs(self, mock_os_system, mock_check_output):
        mock_check_output.return_value = """
        NAME                                READY     STATUS    RESTARTS   AGE
        mytv-e05-pickme                     1/1       Running   0          35d
        prometheus-stack-3169584513-0jk3j   2/2       Running   0          103d
        """
        logs.command_line_runner()
        mock_check_output.assert_called_with(['kubectl', '--context=development', '-n', 'platform', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os_system.assert_called_with('kubectl --context=development -n platform logs -f mytv-e05-pickme  | jq')

