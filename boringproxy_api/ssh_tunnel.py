"""Wrappers for SSHTunnel module"""
from .api import WebAPI
from sshtunnel import SSHTunnelForwarder
from paramiko import RSAKey
from io import StringIO


class Tunnel(SSHTunnelForwarder):
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
        super().__init__(ssh_address_or_host=tunnel_info["server_address"],
                         ssh_port=tunnel_info["server_port"],
                         ssh_username=tunnel_info["username"],
                         ssh_pkey=ssh_pkey,
                         remote_bind_address=("127.0.0.1", tunnel_info["tunnel_port"]),
                         local_bind_address=(client_addr, client_port))

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
        ssh_pkey = PKey().from_private_key(StringIO(tunnel_info["tunnel_private_key"]))
        super().__init__(ssh_address_or_host=tunnel_info["server_address"],
                         ssh_port=tunnel_info["server_port"],
                         ssh_username=tunnel_info["username"],
                         ssh_pkey=ssh_pkey,
                         remote_bind_address=("127.0.0.1", tunnel_info["tunnel_port"]),
                         local_bind_address=(self.__client_addr__, self.__client_port__))
        super(Tunnel, self).start()

    def stop(self):
        """Stops the ssh tunnel and removes the tunnel from boring proxy api server"""
        super(Tunnel, self).stop()
        self.__bp_web_api.delete_tunnel(self.__subdomain__)

    def __del__(self):
        self.stop()
