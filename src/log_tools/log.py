import abc
import logging
import os

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

    @property
    def filter(self):
        return self.args.get('messages', False)

    @property
    def since(self):
        return self.args.get('since', False)


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
        if not self.envs:
            env = ''

        # plutus: _, -i, -c, -q

        # None or unknown supplied use default to apps preferred: _. -q
        elif not env or env not in self.envs:
            env = '-' + self.envs[0]
        else:
            env = '-' + env

        jq = ' ' + self.jq if self.jq and self.filter else ''
        since = ' -s {}'.format(self.since) if self.since else ''
        kubetail_cmd = 'kubetail {a} -t {c} -n {ns}{e}{s}{j} -f'.format(c=self.context, ns=self.namespace, e=env, a=self.app, s=since, j=jq)
        kubectl_cmd = 'kubectl --context={c} --namespace={ns}{e} get pods'.format(c=self.context, ns=self.namespace, e=env)

        if self.dryrun:
            print('Dry run:\n{}\n{}'.format(kubectl_cmd, kubetail_cmd))
        else:
            logging.info(kubetail_cmd)
            # Run command until terminated with SIGTERM
            os.system(kubetail_cmd)
            # Self terminated must be an error
            print('\nFailed: Ensure you have signed into Osprey first with\nosprey user login')


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

        ssh_cmd = 'ssh admin@{}'.format(environments[env])
        cmd = 'tail -f /var/sky/logs/popcorn/{}.log'.format(self.app)

        if self.dryrun:
            print('Dry run:\n{}\n{}'.format(ssh_cmd, cmd))
        else:
            logging.info(cmd)

            try:
                # Run command remotely
                c = Connection(environments[env], user='admin')
                c.run(cmd, pty=True)
            except Exception:
                print('\nConnection closed for', environments[env])
