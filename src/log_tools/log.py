import abc
import logging
import os
import re
from subprocess import STDOUT, check_output, CalledProcessError

from fabric import Connection


class Log(object):
    """Abstract Base Class Definition"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, alias, attributes, cli_arguments):
        """Constructor"""
        self.__alias = alias
        self.app = None
        self.envs = []
        self.args = cli_arguments
        for k, v in attributes.items():
            setattr(self, k, v)

    def __repr__(self):
        return str([(k, v) for k, v in self.__dict__.items()])

    @abc.abstractmethod
    def tail(self, env):
        """Required method"""

    @property
    def alias(self):
        return self.__alias

    @property
    def dryrun(self):
        return self.args.get('dry_run', False)


class KubernetesLog(Log):
    """
    Application on Kubernetes,
    Selected by namespace + env
    """
    def __init__(self, alias, attributes, cli_arguments):
        self.context = ''
        self.namespace = ''
        self.jq = None
        super().__init__(alias, attributes, cli_arguments)

    def __repr__(self):
        return "Kubernetes log: %s>" % super().__repr__()

    def tail(self, env):
        # mytv  : _
        if not self.envs: env = ''

        # plutus: _, -i, -c, -q

        # None or unknown supplied use default to apps preferred: _. -q
        elif not env or env not in self.envs:
            env = '-' + self.envs[0]
        else:
            env = '-' + env

        cmd = 'kubectl --context={c} -n {ns}{e} get pods'.format(c=self.context, ns=self.namespace, e=env)

        try:
            if self.dryrun:
                print(cmd)
            else:
                logging.info(cmd)
                pods = check_output(cmd.split(), universal_newlines=True, stderr=STDOUT)
                logging.info(pods)

                rgx = re.compile('(' + self.app + r'[^\s]+)')
                pod = rgx.search(pods).group(1)
                logging.info('Using this pod:{}'.format(pod))

                jq = '| jq' if self.jq else ''

                cmd = 'kubectl --context={c} -n {ns}{e} logs -f {p} {j}'.format(c=self.context, ns=self.namespace, e=env, p=pod, j=jq)

                logging.info(cmd)
                os.system(cmd)

        except FileNotFoundError:
            print('FileNotFoundError: ', cmd)

        except CalledProcessError:
            print('Failed: Ensure you have signed into Osprey first with\nosprey user login')


class LegacyLog(Log):
    """
    A legacy platform application,
    ssh tail
    """

    def __init__(self, alias, attributes, cli_arguments):
        super().__init__(alias, attributes, cli_arguments)

    def __repr__(self):
        return "Legacy log: %s>" % super().__repr__()

    def tail(self, env):
        # These environments must have your ssh public key in /home/admin/.ssh/authorized_keys
        environments = {'quality': 'qualwap01.nowtv.dev', 'int': 'intewap01.nowtv.dev'}

        # use default
        if not env or env not in environments:
            env = self.envs[0]

        cmd = 'tail -f /var/sky/logs/popcorn/{}.log'.format(self.app)

        if self.dryrun:
            print(cmd)
        else:
            logging.info(cmd)
            try:
                c = Connection(environments[env], user='admin')
                c.run(cmd, pty=True)
            except Exception:
                print('\nConnection closed for', environments[env])
