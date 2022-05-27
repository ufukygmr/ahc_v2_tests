import networkx as nx
import time

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, setAHCLogLevel, ConnectorTypes, EventTypes, logger
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from adhoccomputing.DistributedAlgorithms.Broadcasting.Broadcasting import ControlledFlooding,BroadcastingEventTypes
import logging

class ApplicationLayer(GenericModel): 
  def on_message_from_bottom(self, eventobj: Event):
    logger.applog(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")

class AdHocNode(GenericModel):
  def on_message_from_top(self, eventobj: Event):
    eventobj.event = EventTypes.MFRT
    self.send_down(eventobj)

  def on_message_from_bottom(self, eventobj: Event):
    eventobj.event = EventTypes.MFRB
    self.send_up(eventobj)

  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
    super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
    # SUBCOMPONENTS
    self.appl = ApplicationLayer("ApplicationLayer", componentinstancenumber, topology=topology)
    self.broadcastservice = ControlledFlooding("ControlledFlooding", componentinstancenumber, topology=topology)
    self.linklayer = GenericLinkLayer("GenericLinkLayer", componentinstancenumber, topology=topology)

    self.components.append(self.appl)
    self.components.append(self.broadcastservice)
    self.components.append(self.linklayer)

    
    # CONNECTIONS AMONG SUBCOMPONENTS
    self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.broadcastservice)
    self.broadcastservice.connect_me_to_component(ConnectorTypes.UP, self.appl)

    self.broadcastservice.connect_me_to_component(ConnectorTypes.DOWN, self.linklayer)
    self.linklayer.connect_me_to_component(ConnectorTypes.UP, self.broadcastservice)

    # Connect the bottom component to the composite component....
    self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
    self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)


def main():
  #NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
  setAHCLogLevel(21)
  #A random geometric graph, undirected and without self-loops
  G = nx.random_geometric_graph(9, 0.5)
  
  
  # G =nx.Graph()
  # G.add_node(0)
  # G.add_node(1)
  # G.add_node(2)
  # G.add_edge(0,1)
  # G.add_edge(1,0)
  # G.add_edge(0,2)
  # G.add_edge(2,0)
  # G.add_edge(1,2)
  # G.add_edge(2,1)

  topo = Topology()
  topo.construct_from_graph(G, AdHocNode, GenericChannel)
  print(str(topo))
  topo.start()
  topo.nodes[0].broadcastservice.trigger_event(Event(None, BroadcastingEventTypes.BROADCAST, "BROADCAST MESSAGE"))
  time.sleep(5)
  topo.exit()

if __name__ == "__main__":
  main()
