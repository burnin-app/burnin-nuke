# menu.py
import nuke
import os

# Example: Add Gizmo to menu
toolbar = nuke.menu("Nodes")
my_menu = toolbar.addMenu("Burnin")

# Add your gizmo
nuke.menu("Nuke").addCommand("Burnin/My Script", "import my_toolset; my_toolset.run()")

# Add Blured
my_menu.addCommand("Burnin Blured", "nuke.createNode('blured')")
my_menu.addCommand("Nyx Write", "nuke.createNode('write_component')")
