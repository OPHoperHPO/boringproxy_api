# You can partially check it out on this demo instance:https://bpdemo.brng.pro
# First of all, register a demo account here: https://boringproxy.io/
from boringproxy_api import Client, ClientConfig

client_config = ClientConfig()

client_config.user = "admin"
client_config.token = "dwaudawiudhauwihdiuaw21312"
client_config.admin_domain = "tunnels.example.com"

bp_client = Client(client_config)
tunnel = bp_client.open_tunnel("test.tunnels.example.com",  # Bind address:port
                               client_addr="127.0.0.1",  # and register tunnel in bp server
                               client_port="8080")
tunnel2 = bp_client.open_tunnel("test2.tunnels.example.com",  # Bind address:port
                               client_addr="127.0.0.1",  # and register tunnel in bp server
                               client_port="8080")

tunnel.start()  # Open ssh tunnel and register it in bp server
tunnel2.start()

all_tunnels = bp_client.get_all_opened_tunnels()  # Get list of all opened tunnels by this client

bp_client.close_tunnel(tunnel)  # Close one tunnel
bp_client.close_all_tunnels()  # Close all tunnels opened by this client

del bp_client  # Unregister client in bp server
