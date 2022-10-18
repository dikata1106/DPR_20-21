#!/usr/bin/python

from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.revent import *
import sys
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

#Parametro fo para modificar
fo = 3

log = core.getLogger()

# Crear un objeto por cada conexion
class ConnectionUp(Event):
    def __init__(self,connection,ofp):
        Event.__init__(self)
        self.connection = connection
        self.dpid = connection.dpid
        self.ofp = ofp
        dpid_str=dpidToStr(self.dpid)

        # Dependiendo del dpid actuar como Ts o como resto de switches
        if(dpid_str[-2:]=="99"):
            self.act_like_Ts()
        else:
            self.act_like_switch(dpid_str)

    def act_like_Ts(self):
        # Definir subred para cada puerto de Ts
        for i in range(fo):
            msg = of.ofp_flow_mod()

            # Necesario para hacer match en paquetes ip
            msg.match.dl_type=0x800

            # Asigna la IP de destino para cada subred
            msg.match.nw_dst = "10.0."+str(i+1)+".0/24"

            # Asigna el puerto de salida
            action = of.ofp_action_output(port=i+1)
            msg.actions.append(action)
            self.connection.send(msg)

            print("Switch Ts y switch %i conectados" % (i+1))

        # Si el trafico no es de tipo IP (p.ej. ARP) inunda los puertos
        msg = of.ofp_flow_mod()
        action = of.ofp_action_output(port = of.OFPP_FLOOD)
        msg.actions.append(action)
        self.connection.send(msg)

    def act_like_switch(self,dpid):
        num_switch = dpid[-2:]

        # En caso de que el destino se encuentre en la subred que corresponde al switch i
        for i in range(fo):
            msg = of.ofp_flow_mod()

            # Necesario para hacer match en paquetes ip
            msg.match.dl_type=0x800

            # Asigna la IP de destino para cada host
            msg.match.nw_dst = "10.0."+num_switch+"."+str(i+1)

            # Para alcanar el host x se utilizara el puerto x+1 (el puerto 1 es para comunicacion con Ts)
            action = of.ofp_action_output(port=i+2)
            msg.actions.append(action)
            self.connection.send(msg)

            print("Switch %s y host %i conectados" %(num_switch,i+1))

        # En caso de que el destino este en otra subred
        for i in range(fo):
            if i+1 != int(num_switch):
                msg = of.ofp_flow_mod()

                # Hace match con los paquetes de tipo IP
                msg.match.dl_type=0x800

                # Asigna la IP de destino (que es una subred, no un host especifico)
                msg.match.nw_dst = "10.0."+str(i+1)+".0/24"

                # Manda el paquete por el puerto 1, hacia Ts
                action = of.ofp_action_output(port=1)
                msg.actions.append(action)
                self.connection.send(msg)

                print("Switch %s y subred %i conectadas" % (num_switch,i+1))

        # Si el trafico no es de tipo IP (p.ej. ARP) inunda los puertos
        msg = of.ofp_flow_mod()
        action = of.ofp_action_output(port = of.OFPP_FLOOD)
        msg.actions.append(action)
        self.connection.send(msg)

class Controlador(object):

    def __init__(self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self,event):
        ConnectionUp(event.connection,event.ofp)
        log.info("Switch %s has come up.", dpid_to_str(event.dpid))

def launch():
    core.registerNew(Controlador)