import nuke
from burnin.entity.surreal import Thing
from burnin.path import get_path_variable_values_to_dict


def create_burnin_sticky_data():
    node = nuke.selectedNode()
    if node:
        data = None
        if node.Class() == "burninRead":
            component_path = node.knob("component_path").value()
            start = node.knob("start").value()
            end = node.knob("end").value()

            key_value = get_path_variable_values_to_dict(component_path)
            path = ""
            for k in key_value.keys():
                path += k + ":" + key_value[k] + " "

            component_thing = Thing.from_str("", component_path)
            component_name = component_thing.name()

            data = f"""{path}
{component_name}
{start}-{end}"""
        elif node.Class() == "burninWrite":
            print("sticky data")
        else:
            print(
                "Not a valid node. Run this by selecting 'Bunrin Read' or 'Burnin Write'"
            )

        if data:
            sticky = nuke.nodes.StickyNote()
            sticky["label"].setValue(data)
            sticky["note_font_size"].setValue(50)

            # Position the sticky above the selected node
            sticky.setXpos(node.xpos())
            sticky.setYpos(node.ypos() - 200)  # 100 pixels above
    else:
        print("Must select 'Burnin Read' or 'Burnin Write'")
