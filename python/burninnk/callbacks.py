import nuke
from burninnk.read import BurninRead
from burninnk.utils import find_upstream_nodes


def beforeRender():
    thisNode = nuke.thisNode()

    if thisNode.Class() != "Write":
        return

    reload_knob = thisNode.knob("reload_read")

    if reload_knob and reload_knob.value():
        reads = find_upstream_nodes(thisNode, "burninRead")

        for r in reads:
            external_reload_knob = r.knob("external_reload")
            if external_reload_knob and external_reload_knob.value():
                BurninRead(r)


nuke.addBeforeRender(beforeRender, nodeClass="Write")
