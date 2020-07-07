import pulumi
from pulumi_azure import core, containerservice

config = pulumi.Config("datahike-web")

resource_group = core.ResourceGroup('datahike')

containers = ([
    {'cpu': 1,
     'image': 'mopedtobias/datahike-server:0.1.0',
     'memory': 1.5,
     'name': 'datahike-server',
     'ports': [{'port': 3000,
                'protocol': 'TCP'}]}])
container = containerservice.Group("datahike-server", containers=containers,
                                   os_type='Linux', resource_group_name=resource_group.name)

pulumi.export("container_id", container.id)
pulumi.export("public_ip", container.ip_address)
