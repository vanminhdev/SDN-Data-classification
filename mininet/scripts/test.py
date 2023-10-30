#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController, Node
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import setLogLevel, info


def myNetwork():
  net = Mininet(topo=None, build=False)

  info('*** Adding controller\n')
  net.addController(name='c0', controller=RemoteController, ip='192.168.0.2', port=6653)

  info('*** Add switches\n')
  s1 = net.addSwitch('s1')

  info('*** Add hosts\n')
  h1 = net.addHost('h1')

  info('*** Add links\n')
  net.addLink(h1, s1)

  info('*** Starting network\n')
  net.start()
  CLI(net)
  net.stop()


if __name__ == '__main__':
  setLogLevel('info')
  myNetwork()
