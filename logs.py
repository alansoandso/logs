#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import re
from subprocess import STDOUT, check_output, CalledProcessError

import yaml
from fabric import Connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def partner_logs(app, env):
    if app.get('legacy', None):
        legacy_logs(app['legacy'], env)
    else:
        kubernetes_logs(app['kubernetes'], env)


def legacy_logs(app, env):
    # These environments must have your ssh public key in /home/admin/.ssh/authorized_keys
    environments = {'quality': 'qualwap01.nowtv.dev',
                    'int': 'intewap01.nowtv.dev'}

    # default to quality
    if not env or env not in environments:
        env = 'quality'

    try:
        c = Connection(environments[env], user='admin')
        c.run('tail -f /var/sky/logs/popcorn/{}.log'.format(app['name']), pty=True)
    except Exception:
        print('\nConnection closed for', environments[env])


def kubernetes_logs(app, env):

    # mytv  : _
    if not app['env']:
        env = ''
    # plutus: _, -i, -c, -q
    # None or quality supplied use default to apps preferred: _. -q
    elif not env or env not in ['int', 'client-int']:
        env = '-' + app['env']
    else:
        env = '-' + env

    try:
        pods = check_output('kubectl --context={c} -n {ns}{e} get pods'.format(c=app['context'], ns=app['namespace'], e=env).split(), universal_newlines=True, stderr=STDOUT)
        logging.info(pods)

        rgx = re.compile('(' + app['app'] + r'[^\s]+)')
        pod = rgx.search(pods).group(1)
        logging.info('Using this pod:{}'.format(pod))

        jq = ' | jq' if app.get('jq', '') else ''
        cmd = 'kubectl --context={c} -n {ns}{e} logs -f {p} {j}'.format(c=app['context'], ns=app['namespace'], e=env, p=pod, j=jq)
        logging.info(cmd)

        os.system(cmd)
    except CalledProcessError:
        print('Failed: Ensure you have signed into Osprey first with\nosprey user login')


def get_parser():
    parser = argparse.ArgumentParser(description='Display logs for apps')
    parser.add_argument('app', action="store", nargs='?', help='app')
    parser.add_argument("-c", "--client_int", action="store_true", default=False, help="Client environment")
    parser.add_argument("-i", "--int", action="store_true", default=False, help="Integration environment")
    parser.add_argument("-j", "--show_apps", action="store_true", default=False, help="Display valid apps")
    parser.add_argument("-q", "--quality", action="store_true", default=False, help="Quality environment")
    return parser


def command_line_runner():
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, 'logs.yml'), 'r') as f:
        apps = yaml.load(f)

    parser = get_parser()
    args = vars(parser.parse_args())

    # Only explicitly set the env if provided
    if args['int']:
        env = 'int'
    elif args['client_int']:
        env = 'client-int'
    elif args['quality']:
        env = 'quality'
    else:
        env = None

    # Display apps for bash completion
    if args['show_apps']:
        for app in apps:
            print(app)
    elif not args['app'] or args['app'] not in apps:
        parser.print_help()
    else:
        partner_logs(apps[args['app']], env)


if __name__ == '__main__':
    command_line_runner()
