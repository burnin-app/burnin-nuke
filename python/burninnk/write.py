import nuke

from burninnk.node import is_connected_to_write
from burnin.api import BurninClient

def BurninWriteV1():
    thisNode = nuke.thisNode()
    node_path = thisNode.knob('component_path').value()
    burnin_client = BurninClient()
    print(burnin_client)

