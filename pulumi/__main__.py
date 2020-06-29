import pulumi
from pulumi import Output
from pulumi_azure import core, compute, network

config = pulumi.Config("datahike-web")
username = config.require("username")
password = config.require("password")

resource_group = core.ResourceGroup("datahike")
net = network.VirtualNetwork(
    "datahike-network",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    address_spaces=["10.0.0.0/16"],
    subnets=[{
        "name": "default",
        "address_prefix": "10.0.1.0/24",
    }])

subnet = network.Subnet(
    "datahike-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=net.name,
    address_prefix="10.0.2.0/24",
    enforce_private_link_endpoint_network_policies="false")
public_ip = network.PublicIp(
    "datahike-ip",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    allocation_method="Dynamic")

network_iface = network.NetworkInterface(
    "datahike-nic",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    ip_configurations=[{
        "name": "webserveripcfg",
        "subnet_id": subnet.id,
        "private_ip_address_allocation": "Dynamic",
        "public_ip_address_id": public_ip.id,
    }])

userdata = """#!/bin/bash
# Install Java
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install -y openjdk-11-jdk
sudo apt-get -y update --fix-missing
sudo apt-get install -y openjdk-11-jdk

# Install datahike-server
sudo wget https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein --output-document=/usr/local/bin/lein
sudo chmod a+x /usr/local/bin/lein
sudo mkdir -p /var/www/datahike-server
cd /var/www/datahike-server
git clone https://github.com/replikativ/datahike-server.git .
sudo chown -R datahike. .
/usr/local/bin/lein uberjar
java -jar ./target/datahike-server-0.1.0-SNAPSHOT-standalone.jar &

sleep 10

if netstat -tulpen | grep 3000
then
  exit 0
fi"""

vm = compute.VirtualMachine(
    "server-vm",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    network_interface_ids=[network_iface.id],
    vm_size="Standard_A2",
    delete_data_disks_on_termination=True,
    delete_os_disk_on_termination=True,
    os_profile={
        "computer_name": "hostname",
        "admin_username": username,
        "admin_password": password,
        "custom_data": userdata,
    },
    os_profile_linux_config={
        "disable_password_authentication": False,
    },
    storage_os_disk={
        "create_option": "FromImage",
        "name": "myosdisk1",
    },
    storage_image_reference={
        "publisher": "canonical",
        "offer": "UbuntuServer",
        "sku": "18.04-LTS",
        "version": "latest",
    })

combined_output = Output.all(vm.id, public_ip.name,
                             public_ip.resource_group_name)
public_ip_addr = combined_output.apply(
    lambda lst: network.get_public_ip(name=lst[1], resource_group_name=lst[2]))
pulumi.export("public_ip", public_ip_addr.ip_address)
