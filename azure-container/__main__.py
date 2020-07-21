import pulumi
import pulumi_azure as azure


config = pulumi.Config()

resource_group = azure.core.ResourceGroup("datahike-resource-group")

virtual_network = azure.network.VirtualNetwork("datahike-network",
                                               address_spaces=["10.0.0.0/16"],
                                               resource_group_name=resource_group.name)

subnet = azure.network.Subnet("datahike-subnet",
                              resource_group_name=resource_group.name,
                              virtual_network_name=virtual_network.name,
                              address_prefixes=["10.0.2.0/24"],
                              service_endpoints=["Microsoft.Storage"])


storage_account = azure.storage.Account("datahikestorage",
                                        resource_group_name=resource_group.name,
                                        account_tier="Standard",
                                        account_replication_type="LRS",
                                        network_rules={"default_action": "Deny",
                                                       "virtual_network_subnet_ids": [subnet.id]},
                                        tags={"environment": "datahike-test"})

containers = ([{'cpu': 1,
                'image': 'mopedtobias/datahike-server:0.1.0',
                'memory': 1.5,
                'name': 'datahike-server',
                'ports': [{'port': 3000,
                           'protocol': 'TCP'}]}])
volumes = ([{'mountPath': '/opt/datahike-server',
             'name': 'datahike-volumes',
             'share_name': 'datahike-volume',
             'storage_account_key': 'datahike',
             'storage_account_name': 'datahike'}])

container = azure.containerservice.Group("datahike-server",
                                         containers=containers,
                                         os_type='Linux',
                                         resource_group_name=resource_group.name,
                                         tags={"environment": "datahike-test"})

pulumi.export("container_id", container.id)
pulumi.export("public_ip", container.ip_address)
