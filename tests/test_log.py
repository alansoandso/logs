from unittest import TestCase
from unittest.mock import patch

from log_tools.log import KubernetesLog
from log_tools.log import LegacyLog


class TestLog(TestCase):
    def setUp(self):
        pass

    def test_KubernetesLog(self):
        kubernetes = KubernetesLog('cmdline-name', {'app': 'partner-accounts-service', 'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'envs': ['int', 'client-int']}, {'dry_run': True})
        assert kubernetes.alias == 'cmdline-name'
        assert kubernetes.app == 'partner-accounts-service'
        assert kubernetes.envs == ['int', 'client-int']
        assert kubernetes.context == 'dev.cosmic.sky'
        assert kubernetes.dryrun

    @patch('log_tools.log.os')
    def test_KubernetesLog_tail(self, mock_os):
        kubernetes = KubernetesLog('partner-accounts', {'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'envs': ['int', 'client-int'], 'app': 'partner-accounts-service', 'jq': False}, {})

        # use int
        kubernetes.tail('int')
        mock_os.system.assert_called_with('kubetail partner-accounts-service -t dev.cosmic.sky -n partner-accounts-int -f ')
        # defaults to int
        kubernetes.tail('unknown')
        mock_os.system.assert_called_with('kubetail partner-accounts-service -t dev.cosmic.sky -n partner-accounts-int -f ')
        # defaults to int
        kubernetes.tail('')
        mock_os.system.assert_called_with('kubetail partner-accounts-service -t dev.cosmic.sky -n partner-accounts-int -f ')

        # use client-int
        kubernetes.tail('client-int')
        mock_os.system.assert_called_with('kubetail partner-accounts-service -t dev.cosmic.sky -n partner-accounts-client-int -f ')

    @patch('log_tools.log.os')
    def test_Kubernetes_logs_mytv_logs(self, mock_os):
        kubernetes = KubernetesLog('mytv', {'context': 'development', 'namespace': 'platform', 'envs': None, 'app': 'mytv-e05', 'jq': '--jq ".message"'}, {'messages': True})
        kubernetes.tail(None)
        mock_os.system.assert_called_with('kubetail mytv-e05 -t development -n platform -f --jq ".message"')

    def test_LegacyLog(self):
        legacy = LegacyLog('cmdline-name', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True}, {})
        assert legacy.alias == 'cmdline-name'
        assert legacy.app == 'services'

    @patch('log_tools.log.Connection')
    def test_LegacyLog_tail(self, mock_connection):
        legacy = LegacyLog('services', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True}, {})
        # mock_connection.return_value = dict(host='qualwap01.nowtv.dev', user='admin')
        # use quality
        legacy.tail('quality')
        mock_connection.assert_called_with('qualwap01.nowtv.dev', user='admin')
        # use quality
        legacy.tail('unknown')
        mock_connection.assert_called_with('qualwap01.nowtv.dev', user='admin')
        # use quality
        legacy.tail('')
        mock_connection.assert_called_with('qualwap01.nowtv.dev', user='admin')
        # use int
        legacy.tail('int')
        mock_connection.assert_called_with('intewap01.nowtv.dev', user='admin')

    @patch('log_tools.log.Connection.run')
    def test_LegacyLog_tail_run(self, mock_run):
        legacy = LegacyLog('services', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True}, {})
        legacy.tail('quality')
        mock_run.assert_called_with('tail -f /var/sky/logs/popcorn/services.log', pty=True)

    @patch('log_tools.log.print')
    def test_LegacyLog_tail_dry_run(self, mock_print):
        legacy = LegacyLog('services', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True}, {'dry_run': True})
        legacy.tail('quality')
        mock_print.assert_called_once()
