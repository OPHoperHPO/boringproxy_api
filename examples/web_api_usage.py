# You can partially check it out on this demo instance:https://bpdemo.brng.pro
# First of all, register a demo account here: https://boringproxy.io/
from boringproxy_api import WebAPI

user = "admin"
token = "fKdawdawdwadawL0awdawdawdawdW"
admin_domain = "tunnels.example.com"

tunnel_server_web_api = WebAPI(admin_domain, user, token)

tunnel_server_web_api.add_user(username="new_user", is_admin=False)  # Create new user. Your account must be admin!
test_user_token = tunnel_server_web_api.add_token("new_user")  # Generate token for new user
tunnel_server_web_api.add_client(owner="new_user", client_name="python")  # Register new client for new_user
all_tunnels = tunnel_server_web_api.get_tunnels()  # Get list of all registered tunnels
tunnel_server_web_api.add_tunnel("data.tunnels.example.com")  # Register new tunnel

tunnel_server_web_api.delete_tunnel("data.tunnels.example.com")
tunnel_server_web_api.delete_token(test_user_token)
tunnel_server_web_api.delete_user("new_user")
