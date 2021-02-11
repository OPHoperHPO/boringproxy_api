"""Wrappers for SSHTunnel module"""
import select
import socket
import threading
from io import StringIO

import paramiko
from paramiko import RSAKey

from .api import WebAPI


def reverse_forward_tunnel(self, server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        if not self.is_alive:
            return
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()


def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    print(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print("Tunnel closed from %r" % (chan.origin_addr,))



class SSHReverseTunnelForwarder:
    """SSH -r Tunnel Forwarder"""

    def __init__(self, hostname, port, username, pkey, server_port, remote_host, remote_port):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.pkey = pkey
        self.server_port = server_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.thread = None
        self.is_alive = False

    def start(self):
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            pkey=self.pkey,
            look_for_keys=False,
        )
        self.thread = threading.Thread(
            target=reverse_forward_tunnel, args=(self, self.server_port, self.remote_host, self.remote_port,
                                                 self.client.get_transport())
        )
        self.thread.setDaemon(True)
        self.thread.start()
        self.is_alive = True

    def stop(self):
        if not self.is_alive:
            raise Exception("Nothing to stop")
        self.is_alive = False


class Tunnel(SSHReverseTunnelForwarder):
    """
    SSHTunnelForwarder Wrapper to communicate with Boring Proxy API server.
    """
    def __init__(self, web_api: WebAPI, subdomain: str, ssh_key_id="", client_name="any", client_addr="127.0.0.1",
                 client_port=5555, allow_external_tcp=False, password_protect=False, username="", password="",
                 tls_termination="server", **kwargs):

        self.__bp_web_api = web_api
        self.__subdomain__ = subdomain + '.' + web_api.admin_domain \
            if '.' + web_api.admin_domain not in subdomain else subdomain
        self.__ssh_key_id__ = ssh_key_id
        self.__client_name__ = client_name
        self.__client_addr__ = client_addr
        self.__client_port__ = client_port
        self.__allow_external_tcp__ = allow_external_tcp
        self.__password_protect__ = password_protect
        self.__username__ = username
        self.__password__ = password
        self.__tls_termination__ = tls_termination
        self.__kwargs__ = kwargs
        tunnel_info = self.__register_tunnel__()
        ssh_pkey = RSAKey.from_private_key(file_obj=StringIO(tunnel_info["tunnel_private_key"]))
        super().__init__(hostname=tunnel_info["server_address"],
                         port=tunnel_info["server_port"],
                         username=tunnel_info["username"],
                         pkey=ssh_pkey,
                         server_port=int(tunnel_info["tunnel_port"]),
                         remote_host=client_addr,
                         remote_port=client_port)

    def __register_tunnel__(self):
        """Registers ssh tunnel in the boring proxy API server"""
        all_tunnels = self.__bp_web_api.get_tunnels(self.__client_name__)
        if self.__subdomain__ not in all_tunnels.keys():
            self.__bp_web_api.add_tunnel(self.__subdomain__,
                                         ssh_key_id=self.__ssh_key_id__, client_name=self.__client_name__,
                                         client_addr=self.__client_addr__,
                                         client_port=self.__client_port__,
                                         allow_external_tcp=self.__allow_external_tcp__,
                                         password_protect=self.__password_protect__, username=self.__username__,
                                         password=self.__password__,
                                         tls_termination=self.__tls_termination__, **self.__kwargs__)
            all_tunnels = self.__bp_web_api.get_tunnels(self.__client_name__)
        tunnel_info = all_tunnels[self.__subdomain__]
        return tunnel_info

    def start(self):
        """Registers a tunnel with a boring proxy api and starts an ssh tunnel"""
        tunnel_info = self.__register_tunnel__()
        ssh_pkey = RSAKey.from_private_key(StringIO(tunnel_info["tunnel_private_key"]))
        super().__init__(hostname=tunnel_info["server_address"],
                         port=tunnel_info["server_port"],
                         username=tunnel_info["username"],
                         pkey=ssh_pkey,
                         server_port=int(tunnel_info["tunnel_port"]),
                         remote_host=self.__client_addr__,
                         remote_port=self.__client_port__)
        super(Tunnel, self).start()

    def stop(self):
        """Stops the ssh tunnel and removes the tunnel from boring proxy api server"""
        super(Tunnel, self).stop()
        self.__bp_web_api.delete_tunnel(self.__subdomain__)

    def __del__(self):
        self.stop()
