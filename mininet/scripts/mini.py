import os
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

net = Mininet(controller=RemoteController, switch=OVSSwitch)

c0 = net.addController('c0', ip='192.168.0.2', port=6653)
#c0 = net.addController('c0')
c0.start()
switch = net.addSwitch('s1')

host1 = net.addHost('h1', ip='192.168.0.21')
host1.cmd('ip route add default via 192.168.0.1')
host2 = net.addHost('h2', ip='192.168.0.22')
host1.cmd('ip route add default via 192.168.0.1')

net.addLink(host1, switch)
net.addLink(host2, switch)

net.start()

os.system('ifconfig eth0 172.31.64.1/24 up')  # Add virtual interface on host

# set mạng internet
#intf = net.get('s1').intf('s1-eth1')  # Interface connecting to host
#intf.setIP('192.168.237.68/24')  # Set IP address on switch interface

# Configure hosts within Mininet
#host1.cmd('ifconfig h1-eth0 0')  # Remove previous IP
#host1.cmd('ip addr add 192.168.237.69/24 dev h1-eth0')  # Set IP address

#host2.cmd('ifconfig h2-eth0 0')  # Remove previous IP
#host2.cmd('ip addr add 192.168.237.70/24 dev h2-eth0')  # Set IP address

CLI(net)
net.stop()
