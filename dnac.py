from dnacentersdk import api

# Create a DNACenterAPI connection object;
# it uses DNA Center sandbox URL, username and password, with DNA Center API version 2.2.2.3.
# and requests to verify the server's TLS certificate with verify=True.
dnac = api.DNACenterAPI()

# Find all devices that have 'Switches and Hubs' in their family
devices = dnac.devices.get_device_list(family='Switches and Hubs')

# Print all of demo devices
for device in devices.response:
    print('{:20s}{}'.format(device.hostname, device.upTime))