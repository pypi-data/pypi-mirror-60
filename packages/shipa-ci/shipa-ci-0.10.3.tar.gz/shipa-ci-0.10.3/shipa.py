#!/usr/bin/env python

import os
import sys
import tempfile
import requests
import tarfile
from gitignore import GitIgnore
import argparse


class ShipaException(Exception):
    pass


class RepositoryFolder(object):
    IGNORE_FILENAME = '.shipaignore'

    def __init__(self, directory, verbose=False):
        assert directory is not None
        assert verbose is not None

        self.directory = directory
        self.verbose = verbose

        ignore_path = os.path.join(directory, self.IGNORE_FILENAME)
        lines = None
        if os.path.isfile(ignore_path) is True:
            with open(ignore_path, 'r') as f:
                lines = f.readlines()
        self.shipa_ignore = GitIgnore(lines or [])

    def create_tarfile(self):

        os.chdir(self.directory)
        if self.verbose: print('Create tar archive:')

        def filter(info):
            if info.name.startswith('./.git'):
                return

            filename = info.name[2:]

            if self.shipa_ignore.match(filename):
                if self.verbose: print('IGNORE: ', filename)
                return

            if self.verbose: print('OK', filename)
            return info

        f = tempfile.TemporaryFile(suffix='.tar.gz')
        tar = tarfile.open(fileobj=f, mode="w:gz")
        tar.add(name='.',
                recursive=True,
                filter=filter)
        tar.close()
        f.seek(0)
        return f


class ShipaClient(object):

    def __init__(self, server, email=None, password=None, token=None, verbose=False):
        self.server = server
        if not server.startswith('http'):
            self.urlbase = 'http://{0}'.format(server)
        else:
            self.urlbase = server

        self.email = email
        self.password = password
        self.token = token
        self.verbose = verbose

    def auth(self):
        if self.email is None or self.password is None:
            raise ShipaException('Please, provide email and password')

        url = '{0}/users/{1}/tokens'.format(self.urlbase, self.email)
        params = {'password': self.password}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        r = requests.post(url, params=params, headers=headers)
        if self.verbose and r.status_code != 200:
            # Print server response only if there is any failure message!!!
            print('Server response: ')
            print(r.text)

        if r.status_code != 200:
            raise ShipaException(r.text)

        self.token = r.json()['token']

    def parse_step_interval(self, step_interval):
        if step_interval.endswith('s'):
            return int(step_interval[:len(step_interval)-1])
        elif step_interval.endswith('m'):
            return int(step_interval[:len(step_interval)-1])*60
        elif step_interval.endswith('h'):
            return int(step_interval[:len(step_interval)-1])*60*60
        elif step_interval == '':
            return 1
        else:
            return step_interval

    def deploy(self, appname, directory, steps, step_interval, step_weight):
        folder = RepositoryFolder(directory, verbose=self.verbose)
        file = folder.create_tarfile()

        url = '{0}/apps/{1}/deploy'.format(self.urlbase, appname)
        headers = {"Authorization": "bearer " + self.token}

        files = {'file': file}
        body = {'kind': 'git', 'steps': steps, 'step-interval': self.parse_step_interval(step_interval), 'step-weight': step_weight}
        r = requests.post(url, files=files, headers=headers, data=body)

        if self.verbose:
            print('Server response:')
            print(r.text)
            print(r.status_code)

        if r.text is None:
            raise ShipaException(r.text)

        ok = any(line.strip() == "OK"
                 for line in r.text.split('\n'))

        if ok is False:
            raise ShipaException(r.text)


def runapp():

    parser = argparse.ArgumentParser(description='Shipa CI tool')
    parser.add_argument('--directory',
                        help='directory to deploy (default .)',
                        default='.')
    parser.add_argument('--app', help='application name', required=True)
    parser.add_argument('--server',
                        help='shipa server, for example http://shipa-ci-integration.org:8080',
                        required=True)
    parser.add_argument('--email', help='user email')
    parser.add_argument('--password', help='user password')
    parser.add_argument('--token', help='token')
    parser.add_argument('--verbose', help='verbose output', default=False, action='store_true')
    parser.add_argument('--steps', help='steps for canary deployment', default=1)
    parser.add_argument('--step-interval', help='single step duration. supported min: m, hour:h, second:s. ex. 1m, 60s, 1h', default='1s')
    parser.add_argument('--step-weight', help='step weight', default=100)
    args = parser.parse_args()

    try:
        client = ShipaClient(server=args.server,
                             email=args.email,
                             password=args.password,
                             token=args.token,
                             verbose=args.verbose)
        if args.token is None:
            client.auth()

        client.deploy(appname=args.app, directory=args.directory, steps = args.steps, step_interval = args.step_interval, step_weight = args.step_weight)

    except ShipaException as e:
        print('We have some a problem: {0}'.format(str(e)))
        sys.exit(1)


if __name__ == '__main__':
    runapp()
