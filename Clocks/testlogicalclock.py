import random
import time
import os
import sys
sys.path.insert(0, os.getcwd())
import networkx as nx

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, ConnectorTypes, setAHCLogLevel, logger
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
import logging
from adhoccomputing.DistributedAlgorithms.Clocks.LogicalClocks import VectorClock, LogicalClockEventTypes


class ApplicationLayerComponent(GenericModel):

  def on_init(self, eventobj: Event):
    logger.info(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")
    if self.componentinstancenumber == 0:
      self.send_down(Event(self, EventTypes.MFRT, None))

  def on_message_from_bottom(self, eventobj: Event):
    randdelay = random.randint(0, 2)
    time.sleep(randdelay)
    self.send_down(Event(self, EventTypes.MFRT, None))  

  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
      super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
 

class AdHocNode(GenericModel):

  def on_init(self, eventobj: Event):
    #print(f"Initializing {self.componentname}.{self.componentinstancenumber}")
    pass
  def on_message_from_top(self, eventobj: Event):
    logger.applog(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")
    self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

  def on_message_from_bottom(self, eventobj: Event):
    logger.info(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")
    self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))


  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
    super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

    # SUBCOMPONENTSc
    self.appllayer = ApplicationLayerComponent("ApplicationLayer", componentinstancenumber, topology=topology)
    self.middleware = VectorClock("VectorClock ", componentinstancenumber, topology=topology)
    self.netlayer = GenericNetworkLayer("NetworkLayer", componentinstancenumber, topology=topology)
    self.linklayer = GenericLinkLayer("LinkLayer", componentinstancenumber, topology=topology)

    self.components.append(self.appllayer)
    self.components.append(self.middleware)
    self.components.append(self.netlayer)
    self.components.append(self.linklayer)

    # CONNECTIONS AMONG SUBCOMPONENTS
    self.appllayer.connect_me_to_component(ConnectorTypes.DOWN, self.middleware)
    self.middleware.connect_me_to_component(ConnectorTypes.UP, self.appllayer)
    self.middleware.connect_me_to_component(ConnectorTypes.DOWN, self.netlayer)
    self.netlayer.connect_me_to_component(ConnectorTypes.UP, self.middleware)
    self.netlayer.connect_me_to_component(ConnectorTypes.DOWN, self.linklayer)
    self.linklayer.connect_me_to_component(ConnectorTypes.UP, self.netlayer)

    # Connect the bottom component to the composite component....
    self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
    self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)
    

def main():
  setAHCLogLevel(21)
  G = nx.random_geometric_graph(3, 1)
  topo = Topology()
  topo.construct_from_graph(G, AdHocNode, GenericChannel)
  topo.start()

  topo.nodes[0].middleware.trigger_event(Event(None, LogicalClockEventTypes.SEND, None))

  time.sleep(5)
  topo.exit()

if __name__ == "__main__":
  main()