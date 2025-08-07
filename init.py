import os
import nuke

print("Burnin Nuke Loaded")

this_dir = os.path.dirname(__file__)
nuke.pluginAddPath(os.path.join(this_dir, "gizmos"))
nuke.pluginAddPath(os.path.join(this_dir, "python"))
nuke.pluginAddPath(os.path.join(this_dir, "icons"))

os.environ["BURNIN_DCC"] = "nuke"