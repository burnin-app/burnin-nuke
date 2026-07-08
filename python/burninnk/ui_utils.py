from typing import Union

import nuke


def enforceFrameRange(first: int, last: int):
    root = nuke.root()
    root["first_frame"].setValue(first)
    root["last_frame"].setValue(last)
    print("Setting Project Frame Range: ", first, "-", last)
    nuke.frame(int(nuke.root()["first_frame"].value()))


def setNodeStatusColor(nodes: Union[nuke.Node, list], status: str):
    if isinstance(nodes, nuke.Node):
        nodes = [nodes]
    color = None

    colors = {
        "success": 0x3FA66CFF,  # #3fa66c
        "error": 0xD9534FFF,  # example red
        "warning": 0xF0AD4EFF,  # example orange
    }

    color = colors.get(status)
    if color is None:
        raise ValueError(f"Unknown status: {status}")
    for node in nodes:
        node["tile_color"].setValue(color)
