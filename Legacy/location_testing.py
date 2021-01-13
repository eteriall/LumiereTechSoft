import json

from ipregistry import IpregistryClient

client = IpregistryClient("tryout")
ipInfo = client.lookup()
ipInfo = json.loads(str(ipInfo))
location_data = ipInfo["location"]
print(ipInfo["ip"])
print(location_data["country"]["flag"]["emoji"], location_data["city"], location_data["latitude"], location_data["longitude"])