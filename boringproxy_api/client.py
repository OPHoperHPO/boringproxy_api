"""Client for Boring Proxy Server"""
from .api import WebAPI
from .ssh_tunnel import Tunnel


class ClientConfig:
    """Config for Client object"""
    admin_domain = ""
    user = "admin"
    token = ""
    client_name = "bp-python-client"


class Client:
    """
    Client for Boring Proxy Server
    """

    def __init__(self, config: ClientConfig):
        self.__config__ = config
        self.__bp_server_api__ = WebAPI(config.admin_domain, config.user, config.token)
        self.__bp_server_api__.add_client(client_name=config.client_name)
        self.__all_opened_tunnels__ = []

    def get_all_opened_tunnels(self):
        """
        Returns all opened tunnels by this client
        :return: list of Tunnels objects
        """
        return self.__all_opened_tunnels__

    def open_tunnel(self, subdomain: str, ssh_key_id="", client_addr="127.0.0.1",
                    client_port=5555, allow_external_tcp=False, password_protect=False, username="", password="",
                    tls_termination="server", **kwargs) -> Tunnel:
        """
        Registers new tunnel and returns Tunnel object
        :return: Tunnel object
        """
        tunnel = Tunnel(self.__bp_server_api__, subdomain, ssh_key_id, self.__config__.client_name,
                        client_addr, client_port,
                        allow_external_tcp, password_protect, username, password, tls_termination, **kwargs)
        self.__all_opened_tunnels__.append(tunnel)
        return tunnel

    def close_tunnel(self, tunnel: Tunnel):
        """
        Closes tunnel
        :param tunnel: Tunnel object
        """
        tunnel.stop()
        self.__all_opened_tunnels__.remove(tunnel)
        return True

    def close_all_tunnels(self):
        """
        Closes all opened tunnels by this client
        """
        list(map(self.close_tunnel, self.__all_opened_tunnels__))

    def __del__(self):
        self.close_all_tunnels()
        self.__bp_server_api__.delete_client(client_name=self.__config__.client_name)
        del self.__bp_server_api__, self.__all_opened_tunnels__, self
