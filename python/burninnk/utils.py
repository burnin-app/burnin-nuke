import os
from pathlib import Path

import nuke
from burnin.entity.utils import (
    node_name_from_component_path,
    parse_node_path,
)

delimeter = "/"
if os.name == "nt":
    delimeter = "\\"


def buildFilePath(include_file_name: bool = False, component_path: str = None):

    node = nuke.thisNode()
    root_path = os.getenv("BURNIN_ROOT_PATH")
    root_name = os.getenv("BURNIN_ROOT_NAME")

    if component_path is None:
        component_path = node.knob("component_path").value()

    node_name = node_name_from_component_path(component_path)
    component_path = parse_node_path(component_path)

    if component_path.startswith("/"):
        component_path = component_path[1:]

    if component_path.startswith("\\"):
        component_path = component_path[1:]

    version_number = node.knob("version").value()

    if include_file_name:
        file_type = node.knob("file_type").value()

        frame_expression = ""
        # check if its time dependent
        if node.knob("timedependent").value() == 1:
            frame_expression = ".####"

        file_name = node_name + frame_expression + file_type

    file_path = Path(root_path) / root_name / component_path / version_number
    if include_file_name:
        return file_path / file_name
    else:
        return file_path


def find_upstream_nodes(start_node, node_class):
    result = []
    visited = set()

    def walk(node):
        if node in visited:
            return
        visited.add(node)

        # Check node type
        if node.Class() == node_class:
            result.append(node)

        # Traverse inputs
        for i in range(node.inputs()):
            upstream = node.input(i)
            if upstream:
                walk(upstream)

    walk(start_node)
    return result
