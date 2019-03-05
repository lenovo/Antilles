# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import json
import time
import logging
import threading
from requests import Response
from Queue import Queue, Empty
from httplib import OK, BAD_REQUEST, INTERNAL_SERVER_ERROR
from requests import Session, HTTPError
from six import add_metaclass
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)

__all__ = ['ConfluentClient', 'ClusterConfluentClient']


@add_metaclass(ABCMeta)
class BaseConfluentClient(object):
    @abstractmethod
    def create_async(self, head, body):
        pass

    @abstractmethod
    def create_ssh_session(self, name, head, body):
        pass

    @abstractmethod
    def create_kvm_console(self, name, head, body):
        pass


class ConfluentClient(BaseConfluentClient):
    def __init__(
            self,
            host='localhost', port='4005',
            user='antilles', password='Passw0rd',
            timeout=30
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.user = user
        self.password = password
        self.session = Session()

    def get_confluent_session(self):
        url = 'http://{}:{}/sessions/current/info'.format(self.host, self.port)
        res = self.session.get(
            url,
            auth=(self.user, self.password),
            headers={'accept': 'application/json'},
            timeout=self.timeout
        )
        try:
            res.raise_for_status()
            if 'confluentsessionid' in res.cookies:
                self.session.cookies['confluentsessionid'] = \
                    res.cookies['confluentsessionid']
        except HTTPError:
            logger.exception(
                'Error while getting confluentsessionid, url is %s',
                url
            )

    def create_ssh_session(self, name, head, body):
        url = 'http://{}:{}/nodes/{}/shell/sessions/'.format(
            self.host, self.port, name
        )
        res = self.session.post(
            url,
            headers=head,
            json=body,
            timeout=self.timeout
        )
        status_code = res.status_code
        if BAD_REQUEST <= status_code < INTERNAL_SERVER_ERROR:
            self.get_confluent_session()
            res = self.session.post(
                url,
                headers=head,
                json=body,
                timeout=self.timeout
            )
        return res

    def create_kvm_console(self, name, head, body):
        url = 'http://{}:{}/nodes/{}/console/session'.format(
            self.host, self.port, name
        )
        res = self.session.post(
            url,
            headers=head,
            json=body,
            timeout=self.timeout
        )
        status_code = res.status_code
        if BAD_REQUEST <= status_code < INTERNAL_SERVER_ERROR:
            self.get_confluent_session()
            res = self.session.post(
                url,
                headers=head,
                json=body,
                timeout=self.timeout
            )
        return res

    def create_async(self, head, body):
        url = 'http://{}:{}/sessions/current/async'.format(
            self.host, self.port
        )
        res = self.session.post(
            url,
            headers=head,
            json=body,
            timeout=self.timeout
        )
        status_code = res.status_code
        if BAD_REQUEST <= status_code < INTERNAL_SERVER_ERROR:
            self.get_confluent_session()
            res = self.session.post(
                url,
                headers=head,
                json=body,
                timeout=self.timeout
            )
        return res


class ConfluentEnv(object):
    def __init__(self):
        self.asyncids = {}
        self.asyncid_lock = threading.Lock()
        # e.g.
        # asyncids = {
        #     "asyncid1": {
        #         "172.20.0.1:4005": asyncid_a,
        #         "172.20.0.2:4005": asyncid_b,
        #         "expiry": time.time() + n
        #  when reach expiry time, this key should be cleared,
        #  also buffs and sessions related to this asyncid should be cleared
        #     }
        #     "asyncid2": {
        #         "172.20.0.1:4005": asyncid_c,
        #         "172.20.0.2:4005": asyncid_d,
        #         "expiry": time.time() + n  # will used later
        #     }
        # }

        self.sessions = {}
        self.session_lock = threading.Lock()
        # e.g.
        # sessions = {
        #     "session1": {"172.20.0.1": session_a, "asyncid": asyncid1},
        #     "session2": {"172.20.0.1": session_b, "asyncid": asyncid1},
        #     "session3": {"172.20.0.2": session_c, "asyncid": asyncid2}
        # }

        self.buffs = {}
        self.buff_lock = threading.Lock()
        # e.g.
        # buffs = {
        #     "asyncid1": collections.deque(),
        #     "asyncid2": collections.deque()
        # }

    def randomstring(self, length=20):
        """Generate a random string of requested length

        :param length: The number of characters to produce, defaults to 20
        """
        chunksize = length / 4
        if length % 4 > 0:
            chunksize += 1
        import base64
        import os
        strval = base64.urlsafe_b64encode(os.urandom(chunksize * 3))
        return strval[0:length - 1]

    def assign_asyncids(self):
        antilles_asyncid = self.randomstring(32)
        while antilles_asyncid in self.asyncids:
            antilles_asyncid = self.randomstring(32)

        with self.asyncid_lock:
            self.asyncids[antilles_asyncid] = {}

        return antilles_asyncid

    def set_asyncids(self, antilles_asyncid, server, real_asyncid):
        with self.asyncid_lock:
            self.asyncids[antilles_asyncid][server] = real_asyncid
            self.asyncids[antilles_asyncid]["expiry"] = time.time() + 180

    def update_asyncids(self, antilles_asyncid):
        with self.asyncid_lock:
            self.asyncids[antilles_asyncid]["expiry"] = time.time() + 180

    def get_asyncids(self, antilles_asyncid):
        return self.asyncids[antilles_asyncid]

    def del_asyncid(self, antilles_asyncid):
        if antilles_asyncid not in self.asyncids:
            return
        with self.asyncid_lock:
            del self.asyncids[antilles_asyncid]

    def assign_sessions(self):
        sessid = self.randomstring(32)
        while sessid in self.sessions:
            sessid = self.randomstring(32)
        with self.session_lock:
            self.sessions[sessid] = {}
        return sessid

    def set_sessions(self, antilles_asyncid, antilles_session, server, real_session):
        with self.session_lock:
            self.sessions[antilles_session][server] = real_session
            self.sessions[antilles_session]["asyncid"] = antilles_asyncid

    def get_sessions(self, antilles_session):
        return self.sessions[antilles_session]

    def del_session(self, antilles_asyncid):
        session = None
        for sess in self.sessions:
            if antilles_asyncid == self.sessions[sess]["asyncid"]:
                session = sess
                break

        if session:
            with self.session_lock:
                del self.sessions[session]

    def write_buff(self, asyncid, content):
        try:
            _cache = content.json()
            if "asyncid" in _cache or "asyncresponse" in _cache:
                with self.buff_lock:
                    if asyncid not in self.buffs:
                        self.buffs[asyncid] = Queue()
                    self.buffs[asyncid].put(content)
        except Exception:
            logger.exception("Error while write buff from confluent.")
            pass

    def clear_buff(self, asyncid):
        try:
            self.buffs[asyncid].queue.clear()
        except Exception:
            pass

    def del_buff(self, antilles_asyncid):
        if antilles_asyncid not in self.buffs:
            return
        with self.buff_lock:
            del self.buffs[antilles_asyncid]

    def read_buff(self, asyncid):
        if asyncid not in self.buffs:
            return None
        ret = None
        try:
            ret = self.buffs[asyncid].get(timeout=30)
        except Empty:
            logger.info(
                "The asyncid: {asyncid} has no cache.".format(asyncid=asyncid))
            ret = Response()
            ret.status_code = 200
            ret._content = json.dumps({"_links": {}})

        except Exception:
            logger.exception("Unknown error occurred while read buffer.")
        return ret

    def clear_cache(self, antilles_asyncid):
        self.del_asyncid(antilles_asyncid)
        self.del_session(antilles_asyncid)
        self.del_buff(antilles_asyncid)


class ClusterConfluentClient(BaseConfluentClient):
    def __init__(
            self, configure, port='4005',
            user='antilles', password='Passw0rd',
            timeout=30
    ):
        self.configure = configure
        self.env = ConfluentEnv()

        self.service_node_info = {
            node.hostip: ConfluentClient(
                host=node.hostip,
                port=port,
                user=user,
                password=password,
                timeout=timeout
            )
            for node in configure.service_nodes
        }

        logger.info('All service_node_info: %r', self.service_node_info)

    def _pickup_client_by_nodename(self, node_name):
        for node in self.configure.node:
            if node.name == node_name:
                service_node = node.service_node
                return (
                    service_node.hostip,
                    self.service_node_info[service_node.hostip]
                )
        else:
            raise Exception('Node: %s does not exist in confluent', node_name)

    def create_ssh_session(self, name, head, body):
        server, client = self._pickup_client_by_nodename(name)

        if 'session' not in body:  # create a new shell
            asyncid = head['CONFLUENTASYNCID']
            real_asynid = self.env.get_asyncids(asyncid)[server]
            head['CONFLUENTASYNCID'] = real_asynid
            result = client.create_ssh_session(name, head, body)
            try:
                result.raise_for_status()
                temp = result.json()
                real_session = temp['session']
                antilles_session = self.env.assign_sessions()
                self.env.set_sessions(
                    asyncid, antilles_session,
                    server, real_session
                )

                temp.update({'session': antilles_session})
                # Modify the res body from confluent
                result._content = json.dumps(temp)
            except Exception:
                logger.error(
                    'Cannot create ssh session on confluent server: %s',
                    server
                )
        else:  # shell receive some data
            antilles_session = body['session']

            try:
                real_session = self.env.get_sessions(antilles_session)[server]
            except KeyError:
                raise Exception('Cannot find session %s', antilles_session)

            body['session'] = real_session
            result = client.create_ssh_session(name, head, body)
            try:
                result.raise_for_status()
                temp = result.json()
                temp.update({'session': antilles_session})
                # Modify the res body from confluent
                result._content = json.dumps(temp)
            except Exception:
                logger.error(
                    'Cannot link ssh session on confluent server: %s',
                    server
                )
        return result

    def create_kvm_console(self, name, head, body):
        server, client = self._pickup_client_by_nodename(name)

        if 'session' not in body:  # create a new shell
            asyncid = head['CONFLUENTASYNCID']
            real_asynid = self.env.get_asyncids(asyncid)[server]
            head['CONFLUENTASYNCID'] = real_asynid
            result = client.create_kvm_console(name, head, body)
            try:
                result.raise_for_status()
                temp = result.json()
                real_session = temp['session']
                antilles_session = self.env.assign_sessions()
                self.env.set_sessions(
                    asyncid, antilles_session,
                    server, real_session
                )

                temp.update({'session': antilles_session})
                # Modify the res body from confluent
                result._content = json.dumps(temp)
            except Exception:
                logger.error(
                    'Cannot create kvm console on confluent server: %s',
                    server
                )
        else:  # shell receive some data
            antilles_session = body['session']
            try:
                real_session = self.env.get_sessions(antilles_session)[server]
            except KeyError:
                raise Exception('Cannot find session %s', antilles_session)

            body['session'] = real_session
            result = client.create_kvm_console(name, head, body)
            try:
                result.raise_for_status()
                temp = result.json()
                temp.update({'session': antilles_session})
                # Modify the res body from confluent
                result._content = json.dumps(temp)
            except Exception:
                logger.error(
                    'Cannot link kvm console on confluent server: %s',
                    server
                )
        return result

    def _get_asyncid_from_confluent(self, server, res):
        if OK != res.status_code:
            return False, None

        asyncid = ''
        try:
            asyncid = res.json().get('asyncid')
        except Exception:
            logger.exception(
                'Error when getting asyncid from confluent %s',
                server
            )

        if len(asyncid) > 0:
            return True, asyncid
        else:
            return False, None

    def _create_asyncid(self, server, antilles_asyncid, head, body):
        confluent_client = self.service_node_info[server]
        ret = confluent_client.create_async(head, body)
        ok, real_asyncid = self._get_asyncid_from_confluent(server, ret)
        if not ok:
            logger.exception('Cannot get asyncid from confluent: %s', server)

        self.env.set_asyncids(antilles_asyncid, server, real_asyncid)
        self.env.write_buff(antilles_asyncid, ret)

    def _create_async(self, server, antilles_asyncid, head, body):
        while True:
            if time.time() > self.env.get_asyncids(antilles_asyncid)['expiry']:
                self.env.clear_cache(antilles_asyncid)
                break

            confluent_client = self.service_node_info[server]
            ret = confluent_client.create_async(head, body)
            self.env.write_buff(antilles_asyncid, ret)

    def create_async(self, head, body):
        if not body.get('asyncid'):
            # get asyncid from all confluent server
            tds = []
            asyncid = self.env.assign_asyncids()
            for server in self.service_node_info:
                # concurrent request
                td = threading.Thread(
                    target=self._create_asyncid,
                    args=(server, asyncid, head, body)
                )
                tds.append(td)
                td.setDaemon(True)
                td.start()

            for td in tds:
                td.join()

            if len(self.env.get_asyncids(asyncid)) - 1 != \
                    len(self.service_node_info):
                raise Exception('Confluent server run in error')

            result = self.env.read_buff(asyncid)
            temp = result.json()
            temp.update({'asyncid': asyncid})
            result._content = json.dumps(temp)

            self.env.clear_buff(asyncid)
            self.env.write_buff(asyncid, result)

            # start async request loop
            async_tds = []
            asyncids = self.env.get_asyncids(asyncid)

            for server in asyncids:
                if server == 'expiry':
                    continue

                real_asyncid = asyncids[server]
                body = body.copy()
                body['asyncid'] = real_asyncid

                # concurrent request
                td = threading.Thread(
                    target=self._create_async,
                    args=(server, asyncid, head.copy(), body.copy())
                )
                async_tds.append(td)
                td.setDaemon(True)
                td.start()
        else:
            asyncid = body.get('asyncid')
            self.env.update_asyncids(asyncid)

        result = self.env.read_buff(asyncid)
        return result
