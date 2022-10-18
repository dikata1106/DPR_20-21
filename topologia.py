#!/usr/bin/env python

from mininet.topo import Topo
import sys

class MyTopo(Topo):
    
    def __init__(self):

        Topo.__init__(self)

        switchList = []
        hostList = []

        # Parametro fo para modificar
        fo = 3

        # Crea el switch Ts y le asigna un dpid 
        #topSwitch = self.addSwitch('Ts', cls=OVSKernelSwitch, dpid="0000000100000000")
        topSwitch = self.addSwitch('Ts', dpid="0000000100000099")

        # Crea fo switches y asigna su numero de switch como dpid
        for i in range(fo):
            switchList.append(self.addSwitch("s"+str(i+1), dpid="00000001000000"+format(i+1, '02')))

        # Crea fo^2 hosts y asigna su nombre e ip correspondiente tal y como se especifica en la documentacion
        for n_switch in range(fo):
            for n_host in range(fo):
                hostList.append(self.addHost("h"+str(n_switch+1)+str(n_host+1), ip="10.0."+str(n_switch+1)+"."+str(n_host+1)+"/16"))

        # Crea un link desde cada switch del nivel inferior hasta Ts
        for switch in switchList:
            self.addLink(topSwitch, switch)

        # Crea un link desde cada host al switch que le corresponde
        for i in range(fo):
            for host in hostList[i*fo:(i+1)*fo]:
                self.addLink(switchList[i], host)

# Da un nombre a la topologia
topos = {'mytopo': (lambda: MyTopo())}