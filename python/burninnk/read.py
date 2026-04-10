import os
from pathlib import Path

import nuke
from burnin.api import BurninClient
from burnin.entity.filetype import Image
from burnin.entity.node import Node
from burnin.entity.surreal import Thing
from burnin.entity.utils import buildDirPathFromVersionNode
from burnin.entity.version import Version


def BurninRead(node=None):
    thisNode = nuke.thisNode()
    if node:
        thisNode = node
    read_node = thisNode.input(0)
    node_class = read_node.Class()

    if node_class != "Read":
        nuke.message("❌ Upstream node should be a Read Node")
        return None

    root_id = os.environ.get("BURNIN_ROOT_ID")
    root_path = os.environ.get("BURNIN_ROOT_PATH")
    root_name = os.environ.get("BURNIN_ROOT_NAME")

    if root_path is None:
        print("No root path found")
        return None
    if root_id is None:
        print("No root id found")
        return None
    if root_name is None:
        print("No root name found")
        return None

    burnin_client = BurninClient(nuke._burnin_client)
    component_path = thisNode.knob("component_path").value()
    if component_path.endswith("/"):
        component_path = component_path[:-1]

    version_type = thisNode.knob("version_type").value()
    if version_type == "Version":
        version_number = thisNode.knob("version").value()
    else:
        version_number = version_type

    component_id = Thing.from_ids(root_id, component_path + "/" + version_number)

    try:
        burnin_client = BurninClient()
        version_node: Node
        try:
            version_node = burnin_client.get_version_node(component_id)

            if not version_node.node_type.variant_name == "Version":
                raise Exception(
                    f"Invalid node type: {version_node.node_type.variant_name}"
                )

            print("Loading node:", version_node.id.get_id())

            node_file_path = buildDirPathFromVersionNode(
                version_node, root_path, root_name
            )
            node_type: Version = version_node.node_type.data
            file_type = node_type.file_type.data
            if isinstance(file_type, Image):
                file_path = node_file_path / file_type.file_name
                file_path = file_path.as_posix()
                read_node["file"].setValue(file_path)
                thisNode["file"].setValue(file_path)

                print("Read Image File: ", file_path)

                if node_type.comment:
                    thisNode["comment"].setValue(node_type.comment)

                if file_type.time_dependent:
                    frame_range = file_type.frame_range
                    if len(frame_range) == 3:
                        start = int(frame_range[0])
                        end = int(frame_range[1])
                        read_node["first"].setValue(start)
                        read_node["last"].setValue(end)
                        read_node["origfirst"].setValue(start)
                        read_node["origlast"].setValue(end)
                        thisNode["start"].setValue(start)
                        thisNode["end"].setValue(end)
            else:
                raise Exception(
                    f"Node is not an Image Type: {version_node.node_type.variant_name}"
                )

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
