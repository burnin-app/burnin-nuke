# menu.py
import os

import nuke

# Example: Add Gizmo to menu
toolbar = nuke.menu("Nodes")
burnin_menu = toolbar.addMenu("Burnin")

# Add your gizmo
nuke.menu("Nuke").addCommand("Burnin/My Script", "import my_toolset; my_toolset.run()")

# create a write node and then create burnin write node
burnin_menu.addCommand(
    "Burnin Write",
    "nuke.createNode('Write'); nuke.createNode('burninWrite'); nuke.connectNodes('Write', 'burninWrite')",
)
# burnin read
burnin_menu.addCommand(
    "Burnin Read",
    "nuke.createNode('Read'); nuke.createNode('burninRead'); nuke.connectNodes('Read', 'burninRead')",
)


def setup_burnin():
    node = nuke.thisNode()
    root_path = os.environ.get("BURNIN_ROOT_PATH")
    root_name = os.environ.get("BURNIN_ROOT_NAME")
    root_id = os.environ.get("BURNIN_ROOT_ID")
    node["RootName"].setValues([root_name])


nuke.addOnUserCreate(setup_burnin, nodeClass="burninRead")
