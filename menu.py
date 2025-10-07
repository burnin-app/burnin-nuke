# menu.py
import nuke
import os

# Example: Add Gizmo to menu
toolbar = nuke.menu("Nodes")
burnin_menu = toolbar.addMenu("Burnin")

# Add your gizmo
nuke.menu("Nuke").addCommand("Burnin/My Script", "import my_toolset; my_toolset.run()")

# create a write node and then create burnin write node
burnin_menu.addCommand("Burnin Write", "nuke.createNode('Write'); nuke.createNode('burninWrite'); nuke.connectNodes('Write', 'burninWrite')")
