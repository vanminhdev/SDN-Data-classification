from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, Docker
from mininet.cli import CLI

class MyTopology(Topo):
  def build(self):
    # Thêm switch
    switch = self.addSwitch('s1')

    # Thêm host
    host = self.addHost('h1')
    
    # Kết nối host và switch
    self.addLink(host, switch)

topo = MyTopology()
net = Mininet(topo=topo, controller=RemoteController)
net.start()

# Cấu hình IP cho host
host = net.get('h1')
host.cmd('ifconfig h1-eth0 10.0.0.2 netmask 255.255.255.0')

# Cấu hình default gateway
host.cmd('route add default gw 10.0.0.1')

# Thiết lập NAT trên switch (cần cài đặt mininet có hỗ trợ NAT)
switch = net.get('s1')
switch.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
switch.cmd('iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')

CLI(net)
net.stop()
