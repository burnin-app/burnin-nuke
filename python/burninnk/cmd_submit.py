import os
from pathlib import Path

import nuke
from burnin.api import BurninClient
from burnin.entity.filetype import FileType
from burnin.entity.media import FfmpegCMD
from burnin.entity.node import Node
from burnin.entity.queue import CmdSubmit
from burnin.entity.surreal import Thing
from burnin.entity.utils import (
    TypeWrapper,
    node_name_from_component_path,
    parse_node_path,
)
from burnin.entity.version import Version, VersionStatus
from burninnk.utils import buildFilePath


def submit_render_job():
    thisNode = nuke.thisNode()
    root_id = os.getenv("BURNIN_ROOT_ID")
    root_path = os.getenv("BURNIN_ROOT_PATH")
    root_name = os.getenv("BURNIN_ROOT_NAME")

    write_node = thisNode.input(0)
    write_node_name = write_node.name()
    print(write_node_name)
    node_class = write_node.Class()

    if node_class != "Write":
        nuke.message("❌ Upstream node should be a Write Node")
        return None

    component_path = thisNode.knob("component_path").value()
    component_id = Thing.from_ids(root_id, component_path + "/v000")
    version_node = Node.new_version(component_id, FileType.Image)

    burnin_client = BurninClient(nuke._burnin_client)

    try:
        version_node: Node = burnin_client.create_or_update_component_version(
            version_node
        )
        version_node_id = version_node.get_node_id_str()
        version_number = version_node_id.split("/")[-1]
        thisNode.knob("version").setValue(version_number)

        limit_range = thisNode.knob("limit_to_range").value()
        write_node.knob("use_limit").setValue(limit_range)

        start = 0
        end = 0
        if limit_range:
            # start = thisNode.knob("start").value()
            start = thisNode.knob("start").value()
            write_node.knob("first").setValue(int(start))

            end = thisNode.knob("end").value()
            write_node.knob("last").setValue(int(end))

        frame_range_arg = f"{int(start)}-{int(end)}"
        file_path = buildFilePath(include_file_name=False)

        # TODO: need to change this for unix
        file_path_split = str(file_path).split("\\")
        file_name = node_name_from_component_path(version_node.id.id.String)

        if limit_range:
            file_name_from_path = file_name + ".####.exr"
            thumbnail_frame_number = str(int(start)).zfill(4)
            thumbnail_file_name = file_name + "." + thumbnail_frame_number + ".exr"
        else:
            file_name_from_path = file_name + ".exr"
            thumbnail_file_name = file_name_from_path

        setup_file_name = file_name + "_render_setup" + ".nk"
        setup_path = file_path / setup_file_name

        file_path = str(file_path) + "\\" + file_name_from_path

        # for sending into thumbnail path
        image_file_path = file_path.replace(file_name_from_path, thumbnail_file_name)

        output_file_path = image_file_path.replace(thumbnail_file_name, "thumbnail.png")

        ffmpeg = FfmpegCMD(image_file_path, output_file_path)

        file_path = file_path.replace("\\", "/")
        thisNode.knob("dir_path").setValue(file_path)

        ## set wirite node path
        write_node.knob("file").setValue(str(file_path))
        write_node.knob("file_type").setValue(3)  # set exr

        wace = thisNode.knob("write_ACES_compliant_EXR").value()
        write_node.knob("write_ACES_compliant_EXR").setValue(wace)

        thisNode.knob("status").setValue(VersionStatus.Incomplete.value)
        file_type = ".exr"

        # save script
        nuke.scriptSave()
        print(setup_path)
        nuke.scriptSaveAs(str(setup_path))

        stack = os.getenv("BU_STACK")

        node_names = str(version_node.id.id.String).split("/")
        job_names = []
        for n in node_names:
            if ":" in n:
                name = n.split(":")[-1]
                job_names.append(name)

        if len(node_names) > 2:
            job_names.append(node_names[-2])
            job_names.append(node_names[-1])
        job_name = "_".join(job_names)

        nuke_version = "Nuke" + str(nuke.NUKE_VERSION_STRING).split("v")[0] + ".exe"
        cmd = CmdSubmit.new(
            name=job_name,
            shell=nuke_version,
            component_id=version_node.id,
            cwd=None,
            env={},
            args=[
                "--nukex",
                "-x",
                "-X",
                write_node_name,
                "-F",
                frame_range_arg,
                str(setup_path),
            ],
            stack=stack,
            frame_range=[int(start), int(end)],
            user_id=None,
            output_path=str(file_path),
            comment=None,
            dcc=nuke_version,
        )

        # print(cmd)
        burnin_client.cmd_submit(cmd)

    except Exception as e:
        print(str(e))
