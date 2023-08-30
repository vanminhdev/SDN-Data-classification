import os
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.cli import CLI

switches = {}
controllers = {}
hosts = {}

net = Mininet(controller=Controller, switch=OVSSwitch, waitConnected=False)

for i in range(1, 9):
    host_name = 'h{}'.format(i)
    hosts[host_name] = net.addHost(host_name)

# Adding switches
for i in range(1, 9):
    switch_name = 's{}'.format(i)
    switches[switch_name] = net.addSwitch(switch_name, protocols='OpenFlow13')

# Add links
net.addLink(hosts['h1'], switches['s1'])
net.addLink(hosts['h2'], switches['s2'])
net.addLink(hosts['h3'], switches['s3'])
net.addLink(hosts['h4'], switches['s4'])
net.addLink(hosts['h5'], switches['s5'])
net.addLink(hosts['h6'], switches['s6'])
net.addLink(hosts['h7'], switches['s7'])
net.addLink(hosts['h8'], switches['s8'])

net.addLink(switches['s1'], switches['s2'])
net.addLink(switches['s2'], switches['s3'])
net.addLink(switches['s3'], switches['s4'])
net.addLink(switches['s4'], switches['s1'])

net.addLink(switches['s4'], switches['s5'])

net.addLink(switches['s5'], switches['s6'])
net.addLink(switches['s6'], switches['s7'])
net.addLink(switches['s7'], switches['s8'])
net.addLink(switches['s8'], switches['s5'])

#    s1 - s2
#    |     |   c1
#    s4 - s3
#    |
#    s5 - s6
#    |    |    c2
#    s8 - s7

# Map switches and controller
# map_switch_controller = {
#    'c1': ['s3', 's4']
# }

controllers['c1'] = net.addController('c1', controller=RemoteController, ip='192.168.0.2', port=6653)
controllers['c2'] = net.addController('c2', controller=RemoteController, ip='192.168.0.3', port=6653)

for key in controllers.keys():
    controllers[key].start()

#for ctl in map_switch_controller.keys():
#    for swt in map_switch_controller[ctl]:
#	print(ctl, swt)
#	switches[swt].start([controllers[ctl]])

#switches["s1"].stop()
switches["s1"].start([controllers["c1"]])
switches["s2"].start([controllers["c1"]])
switches["s3"].start([controllers["c1"]])
switches["s4"].start([controllers["c1"]])

switches["s5"].start([controllers["c2"]])
switches["s6"].start([controllers["c2"]])
switches["s7"].start([controllers["c2"]])
switches["s8"].start([controllers["c2"]])

#net.start() #start toan bo switch, k nen dung lenh nay

#CLI(net)
#net.stop()
# link s1 s2 down
# link s1 s2 up
# sudo -E python demo.py