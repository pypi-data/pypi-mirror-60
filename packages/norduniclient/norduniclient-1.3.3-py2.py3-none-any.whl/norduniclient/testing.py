# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
import time
import atexit
import random
import subprocess
import base64
import json
from os import environ
from socket import error as SocketError

try:
    from http import client as http
except ImportError:
    import httplib as http

from norduniclient.core import init_db

__author__ = 'lundberg'

# Run tests with different Neo4j docker image versions using environment variables
NEO4J_VERSION = environ.get('NEO4J_VERSION', 'latest')


class Neo4jTemporaryInstance(object):
    """
    Singleton to manage a temporary Neo4j instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.

    """
    _instance = None
    _http_port = None
    _bolt_port = None

    DEFAULT_USERNAME = 'neo4j'
    DEFAULT_PASSWORD = 'neo4j'

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self, neo4j_version=NEO4J_VERSION):
        while self._http_port == self._bolt_port:
            self._http_port = random.randint(40000, 50000)
            self._bolt_port = random.randint(40000, 50000)
        self._docker_exc = 'docker'
        self._docker_name = 'neo4j-{!s}'.format(self.bolt_port)
        try:
            self._process = subprocess.Popen([self._docker_exc, 'run', '--rm', '--name',
                                              '{!s}'.format(self._docker_name),
                                              '-p', '{!s}:7474'.format(self.http_port),
                                              '-p', '{!s}:7687'.format(self.bolt_port),
                                              'neo4j:{}'.format(neo4j_version)],
                                             stdout=open('/tmp/neo4j-temp.log', 'wb'),
                                             stderr=subprocess.STDOUT)
        except OSError:
            assert False, "No docker executable found"

        self._host = 'localhost'

        for i in range(300):
            time.sleep(0.5)
            try:
                if self.change_password():
                    self._db = init_db('bolt://{!s}:{!s}'.format(self.host, self.bolt_port), username='neo4j',
                                       password='testing', encrypted=False)
            except SocketError:
                continue
            else:
                break
        else:
            self.shutdown()
            assert False, 'Cannot connect to the neo4j test instance'

    @property
    def db(self):
        return self._db

    @property
    def host(self):
        return self._host

    @property
    def http_port(self):
        return self._http_port

    @property
    def bolt_port(self):
        return self._bolt_port

    def purge_db(self):
        q = """
            MATCH (n:Node)
            OPTIONAL MATCH (n)-[r]-()
            DELETE n,r
            """
        with self.db.session as s:
            s.run(q)

    def change_password(self, new_password='testing'):
        """
        Changes the standard password from neo4j to testing to be able to run the test suite.
        """
        basic_auth = '%s:%s' % (self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)
        try:  # Python 2
            auth = base64.encodestring(basic_auth)
        except TypeError:  # Python 3
            auth = base64.encodestring(bytes(basic_auth, 'utf-8')).decode()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Basic %s" % auth.strip()
        }

        response = None
        retry = 0
        while not response:  # Retry if the server is not ready yet
            time.sleep(1)
            con = http.HTTPConnection('{!s}:{!s}'.format(self.host, self.http_port), timeout=10)
            try:
                con.request('GET', 'http://{!s}:{!s}/user/{!s}'.format(self.host, self.http_port,
                                                                       self.DEFAULT_USERNAME), headers=headers)
                response = json.loads(con.getresponse().read().decode('utf-8'))
            except (ValueError, http.HTTPException):
                con.close()
            retry += 1
            if retry > 20:
                print("Could not change password for user neo4j")
                con.close()
                return False
        if response and response.get('password_change_required'):
            payload = json.dumps({'password': new_password})
            con.request('POST', 'http://{!s}:{!s}/user/{!s}/password'.format(
                self.host, self.http_port, self.DEFAULT_USERNAME), payload, headers)
            con.close()
        return True

    def shutdown(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None


class Neo4jTestCase(unittest.TestCase):
    """
    Base test case that sets up a temporary Neo4j instance
    """

    neo4j_instance = Neo4jTemporaryInstance.get_instance()
    neo4jdb = neo4j_instance.db

    def tearDown(self):
        self.neo4j_instance.purge_db()

