#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os

import yaml

from log_tools.log import KubernetesLog
from log_tools.log import LegacyLog

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def load_config(args):
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, 'logs.yaml'), 'r') as f:
        apps_yaml = yaml.load(f, Loader=yaml.BaseLoader)

    apps = {}
    for name, config in apps_yaml.items():
        log_class = get_class(config['class'])
        apps[name] = log_class(name, config['app'], args)

    return apps


def get_class(log_type):
    # Mapping of the log type to class
    classes = {'kubernetes': KubernetesLog, 'legacy': LegacyLog}
    return classes[log_type]  # return getattr(sys.modules[__name__], log_type)


def get_parser():
    parser = argparse.ArgumentParser(description='Display logs for apps')
    parser.add_argument('app', action='store', nargs='?', help='app')
    parser.add_argument('-c', '--client_int', action='store_true', default=False, help='Client environment')
    parser.add_argument('-d', '--dry_run', action='store_true', default=False, help='Dry run to show commands')
    parser.add_argument('-g', '--gift_int', action='store_true', default=False, help='Gifting Integration environment')
    parser.add_argument('-i', '--int', action='store_true', default=False, help='Integration environment')
    parser.add_argument('-j', '--show_apps', action='store_true', default=False, help='Display valid apps')
    parser.add_argument('-m', dest='messages', action='store_false', default=True, help='Output no messages with jq')
    parser.add_argument('-s', action='store', dest='since', help='kubetail output since')
    parser.add_argument('-q', '--quality', action='store_true', default=False, help='Quality environment')
    return parser


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    apps = load_config(args)

    # Only explicitly set the env if provided
    if args['int']:
        env = 'int'
    elif args['client_int']:
        env = 'client-int'
    elif args['quality']:
        env = 'quality'
    elif args['gift_int']:
        env = 'gift_int'
    else:
        env = None

    # Display apps for bash completion
    if args['show_apps']:
        for app in apps:
            print(app)
    elif not args['app'] or args['app'] not in apps:
        parser.print_help()
    else:
        apps[args['app']].tail(env)


if __name__ == '__main__':
    command_line_runner()
