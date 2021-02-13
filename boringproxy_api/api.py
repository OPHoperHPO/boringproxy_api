"""Boring Proxy Server HTTP API Wrapper"""
import json
import requests
from .exceptions import MethodNotAllowed, get_exception


class WebAPI:
    """Boring Proxy Server HTTP API wrapper"""

    def __init__(self, admin_domain, user="admin", token=""):
        self.__endpoint_url__ = "https://" + admin_domain + "/api/"
        self.__user__ = user
        self.__token__ = token
        self.admin_domain = admin_domain

    def api_request(self, method: str, path: str, params: dict, is_webui_hack=False, **kwargs):
        """
        Sends a request to the Boring Proxy Server API methods
        :param method: Http request method
        :param path: The path where to send the request
        :param params: Parameters for sending
        :param is_webui_hack: Defines the method used to send the request: to the official API
        or to the web interface API if the method is not yet implemented in the official API
        :param kwargs: Other parameters for the request function in the requests library.
        :return: JSON with server response
        :raises exceptions in .exceptions if something went wrong on the server
        """
        headers = {"Authorization": "bearer " + self.__token__}
        if method in ["GET", "POST", "DELETE", "PUT"]:
            if is_webui_hack:  # TODO Remove this hack with normal API method when issue #56, #57 will be fixed
                data = requests.request(url="https://" + self.admin_domain + "/" + path, headers=headers,
                                        params=params,
                                        method=method, allow_redirects=False, **kwargs)
            else:
                data = requests.request(url=self.__endpoint_url__ + path, headers=headers, params=params,
                                        method=method, **kwargs)
        else:
            raise MethodNotAllowed("Invalid Method")

        if data.status_code == 200:  # All ok
            try:
                return data.json()
            except json.JSONDecodeError:
                return data.text
        elif data.status_code == 303:  # TODO Remove this hack with normal API method when issue #56, #57 will be fixed
            return True
        else:  # Error occurred
            raise get_exception(data)

    def get_tunnels(self, client_name="", **kwargs) -> dict:
        """
        Gets a list of all tunnels for this client
        :param client_name: Client name
        :param kwargs: Other optional parameters for the method
        :return: JSON with server response
        """
        if client_name != "":
            params = {"client-name": client_name}
        else:
            params = {}
        params.update(kwargs)
        return self.api_request("GET", "tunnels", params)

    def add_tunnel(self, subdomain: str,
                   owner="",
                   ssh_key_id="",
                   client_name="any", client_addr="127.0.0.1", client_port=5555,
                   allow_external_tcp=False,
                   password_protect=False, username="", password="",
                   tls_termination="server", **kwargs):
        """
        Registers a new tunnel
        :param subdomain: Subdomain for the admin_domain on which the tunnel will be
        :param owner: The user who owns this tunnel
        :param ssh_key_id: Ssh key id
        :param client_name: The name of the client to assign this tunnel to
        :param client_addr: The address on the client's computer that you want to forward
        :param client_port: The port on the client computer that you want to forward
        :param allow_external_tcp: Enable raw TCP tunneling for other protocols than HTTP
        :param password_protect: Enable to set username and password for HTTP basic auth
        :param username: HTTP basic auth username
        :param password: HTTP basic auth password
        :param tls_termination: Proxy mode
        :param kwargs: Other optional parameters for this API method
        """
        if '.' + self.admin_domain not in subdomain:
            subdomain = subdomain + '.' + self.admin_domain
        params = {"domain": subdomain,
                  "owner": self.__user__ if owner == "" else owner,
                  "ssh_key_id": ssh_key_id,
                  "client-name": client_name,
                  "client-addr": client_addr,
                  "client-port": str(client_port),
                  "allow-external-tcp": "on" if allow_external_tcp else "off",
                  "password-protect": "on" if password_protect else "off",
                  "username": username,
                  "password": password,
                  "tls-termination": tls_termination}

        params.update(kwargs)
        self.api_request("POST", "tunnels", params)

    def delete_tunnel(self, subdomain: str, **kwargs):
        """
        Removes the tunnel
        :param subdomain: Subdomain on the admin_domain where the tunnel is located
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        if '.' + self.admin_domain not in subdomain:
            subdomain = subdomain + '.' + self.admin_domain
        params = {"domain": subdomain}
        params.update(kwargs)
        self.api_request("DELETE", "tunnels", params)

    def add_user(self, username: str, is_admin=False, **kwargs):
        """
        Adds a user (Only for admins accounts)
        :param username: User name
        :param is_admin: Determines if this user will be an administrator (only for admin tokens)
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        if len(username) < 6:
            raise ValueError("Username must be at least 6 characters")
        params = {"username": username, "is-admin": "on" if is_admin else "off"}
        params.update(kwargs)
        self.api_request("POST", "users/", params)

    def delete_user(self, username: str, **kwargs):
        """
        Removes a user. (Only for admins accounts)
        :param username: User name
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        params = {"username": username}
        params.update(kwargs)
        # TODO Replace this hack with normal API method when issue #57 will be fixed
        self.api_request("POST", "delete-user", params, is_webui_hack=True)

    def add_client(self, owner: str = "", client_name: str = "python_api_client", **kwargs):
        """
        Adds a new client on the server
        :param owner: Account that the client will be listed on
        :param client_name: Client name
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        params = kwargs
        self.api_request("PUT", "users/" + (self.__user__ if owner == "" else owner) + "/clients/" + client_name,
                         params)

    def delete_client(self, owner: str = "", client_name: str = "python_api_client", **kwargs):
        """
        Removes the client on the server
        :param owner: The account where the client is listed
        :param client_name: Client name
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        params = kwargs
        self.api_request("DELETE",
                         "users/" + (self.__user__ if owner == "" else owner) + "/clients/" + client_name,
                         params)

    def add_token(self, owner: str = "", **kwargs):
        """
        Adds a token for an account
        :param owner: Account login
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        params = {"owner": (self.__user__ if owner == "" else owner)}
        params.update(kwargs)
        return self.api_request("POST", "tokens/", params)

    def delete_token(self, token: str, **kwargs):
        """
        Removes the access token from the account
        :param token: Account token
        :param kwargs: Other optional parameters for this API method
        :return: JSON with server response
        """
        params = {"token": token}
        params.update(kwargs)
        # TODO Replace this hack with normal API method when issue #56 will be fixed
        self.api_request("GET", "delete-token", params, is_webui_hack=True)
