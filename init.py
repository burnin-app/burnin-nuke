import os

import nuke

print("Burnin Nuke Loaded")

this_dir = os.path.dirname(__file__)
nuke.pluginAddPath(os.path.join(this_dir, "gizmos"))
nuke.pluginAddPath(os.path.join(this_dir, "python"))
nuke.pluginAddPath(os.path.join(this_dir, "icons"))

os.environ["BURNIN_DCC"] = "nuke"

import burninnk.callbacks


# def beforeRender():
#     thisNode = nuke.thisNode()
#     if thisNode.Class() == "Write":
#         reload_knob = thisNode.knob("reload_read")
#         if reload_knob.value():
#             reads = find_upstream_nodes(thisNode, "burninRead")
#             for r in reads:
#                 BurninRead(r)


# nuke.addBeforeRender(beforeRender, nodeClass="Write")
