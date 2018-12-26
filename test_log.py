from unittest import TestCase
from unittest.mock import patch

from log import KubernetesLog
from log import LegacyLog


class TestLog(TestCase):
    def setUp(self):
        pass

    def test_KubernetesLog(self):
        kubernetes = KubernetesLog('cmdline-name',
                                   {'app': 'partner-accounts-service', 'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'envs': ['int', 'client-int']})
        assert kubernetes.alias == 'cmdline-name'
        assert kubernetes.app == 'partner-accounts-service'
        assert kubernetes.envs == ['int', 'client-int']
        assert kubernetes.context == 'dev.cosmic.sky'

    @patch('log.check_output')
    @patch('log.os')
    def test_KubernetesLog_tail(self, mock_os, mock_check_output):
        kubernetes = KubernetesLog('partner-accounts',
                                   {'context': 'dev.cosmic.sky', 'namespace': 'partner-accounts', 'envs': ['int', 'client-int'], 'app': 'partner-accounts-service',
                                    'jq': True})
        mock_check_output.return_value = """
        NAME                                        READY     STATUS    RESTARTS   AGE
        partner-accounts-service-me-me-me           1/1       Running   0          2h
        partner-accounts-service-75f66cc6f6-sw62w   1/1       Running   0          2h
        """

        # use int
        kubernetes.tail('int')
        mock_check_output.assert_called_with(['kubectl', '--context=dev.cosmic.sky', '-n', 'partner-accounts-int', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=dev.cosmic.sky -n partner-accounts-int logs -f partner-accounts-service-me-me-me | jq')
        # defaults to int
        kubernetes.tail('unknown')
        mock_check_output.assert_called_with(['kubectl', '--context=dev.cosmic.sky', '-n', 'partner-accounts-int', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=dev.cosmic.sky -n partner-accounts-int logs -f partner-accounts-service-me-me-me | jq')
        # defaults to int
        kubernetes.tail('')
        mock_check_output.assert_called_with(['kubectl', '--context=dev.cosmic.sky', '-n', 'partner-accounts-int', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=dev.cosmic.sky -n partner-accounts-int logs -f partner-accounts-service-me-me-me | jq')

        # use client-int
        kubernetes.tail('client-int')
        mock_check_output.assert_called_with(['kubectl', '--context=dev.cosmic.sky', '-n', 'partner-accounts-client-int', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=dev.cosmic.sky -n partner-accounts-client-int logs -f partner-accounts-service-me-me-me | jq')

    @patch('log.check_output')
    @patch('log.os')
    def test_Kubernetes_logs_mytv_logs(self, mock_os, mock_check_output):
        kubernetes = KubernetesLog('mytv', {'context': 'development', 'namespace': 'platform', 'envs': None, 'app': 'mytv-e05', 'jq': True})
        mock_check_output.return_value = """
        NAME                                READY     STATUS    RESTARTS   AGE
        mytv-e05-pickme                     1/1       Running   0          35d
        prometheus-stack-3169584513-0jk3j   2/2       Running   0          103d
        """
        kubernetes.tail(None)
        mock_check_output.assert_called_with(['kubectl', '--context=development', '-n', 'platform', 'get', 'pods'], stderr=-2, universal_newlines=True)
        mock_os.system.assert_called_with('kubectl --context=development -n platform logs -f mytv-e05-pickme | jq')

    def test_LegacyLog(self):
        legacy = LegacyLog('cmdline-name', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True})
        assert (legacy.alias == 'cmdline-name')
        assert (legacy.app == 'services')

    @patch('log.Connection')
    def test_LegacyLog_tail(self, mock_connection):
        legacy = LegacyLog('services', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True})
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

    @patch('log.Connection.run')
    def test_LegacyLog_tail_run(self, mock_run):
        legacy = LegacyLog('services', {'app': 'services', 'envs': ['quality', 'int'], 'jq': True})
        legacy.tail('quality')
        mock_run.assert_called_with('tail -f /var/sky/logs/popcorn/services.log', pty=True)
