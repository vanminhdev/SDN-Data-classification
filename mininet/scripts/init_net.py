import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Controller, OVSSwitch, RemoteController, Node
from mininet.link import TCLink
from mininet.cli import CLI

os.system("mn -c")

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

switches = {}
controllers = {}
hosts = {}

net = Mininet(controller=Controller, switch=OVSSwitch, waitConnected=False, link=TCLink)

for i in range(1, 9):
    host_name = 'h{}'.format(i)
    hosts[host_name] = net.addHost(host_name)

# Adding switches
for i in range(1, 9):
    switch_name = 's{}'.format(i)
    switches[switch_name] = net.addSwitch(switch_name, protocols='OpenFlow13')

# Add links
net.addLink(hosts['h1'], switches['s1'], bw=10)
net.addLink(hosts['h2'], switches['s2'], bw=10)
net.addLink(hosts['h3'], switches['s3'], bw=10)
net.addLink(hosts['h4'], switches['s4'], bw=10)
net.addLink(hosts['h5'], switches['s5'], bw=10)
net.addLink(hosts['h6'], switches['s6'], bw=10)
net.addLink(hosts['h7'], switches['s7'], bw=10)
net.addLink(hosts['h8'], switches['s8'], bw=10)

net.addLink(switches['s1'], switches['s2'], bw=10)
net.addLink(switches['s2'], switches['s3'], bw=10)
net.addLink(switches['s3'], switches['s4'], bw=10)
net.addLink(switches['s4'], switches['s1'], bw=10)

net.addLink(switches['s4'], switches['s5'], bw=10)

net.addLink(switches['s5'], switches['s6'], bw=10)
net.addLink(switches['s6'], switches['s7'], bw=10)
net.addLink(switches['s7'], switches['s8'], bw=10)
net.addLink(switches['s8'], switches['s5'], bw=10)

# hosts1 = [ net.addHost( 'h%d' % n ) for n in ( 3, 4 ) ]
# hosts2 = [ net.addHost( 'h%d' % n ) for n in ( 5, 6 ) ]

# r1 = net.addHost('r1', cls=LinuxRouter, ip='10.1.0.1/24')
# r2 = net.addHost('r2', cls=LinuxRouter, ip='10.2.0.1/24')
# net.addLink(switches['s1'], r1)

#    s1 - s2
#    |     |   c1
#    s4 - s3
#    |
#    s5 - s6
#    |    |    
#    s8 - s7

# Map switches and controller
# map_switch_controller = {
#    'c1': ['s3', 's4']
# }

controllers['c1'] = net.addController('c1', controller=RemoteController, ip='192.168.0.2', port=6653)
controllers['c2'] = net.addController('c2', controller=RemoteController, ip='192.168.0.3', port=6653)

net.build()

for key in controllers.keys():
    controllers[key].start()

#switches["s1"].stop()
switches["s1"].start([controllers["c1"]])
switches["s2"].start([controllers["c1"]])
switches["s3"].start([controllers["c1"]])
switches["s4"].start([controllers["c1"]])

switches["s5"].start([controllers["c1"]])
switches["s6"].start([controllers["c1"]])
switches["s7"].start([controllers["c1"]])
switches["s8"].start([controllers["c1"]])

# Add NAT connectivity
net.addNAT().configDefault()

#net.start() #start toan bo switch, k nen dung lenh nay
#print(hosts['h1'].cmd('dhclient '+ hosts['h1'].defaultIntf().name))
#print(hosts['h1'].cmd('apt update'))
CLI(net)
net.stop()
# link s1 s2 down
# link s1 s2 up
# sudo -E python demo.py