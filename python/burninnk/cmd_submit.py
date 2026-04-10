import os
import shutil
from logging import root
from pathlib import Path

import nuke
from burnin.api import BurninClient
from burnin.entity.filetype import FileType, Image
from burnin.entity.media import FfmpegCMD
from burnin.entity.node import Node
from burnin.entity.queue import CmdSubmit
from burnin.entity.surreal import Thing
from burnin.entity.utils import node_name_from_component_path
from burnin.entity.version import Version, VersionStatus
from burninnk.utils import buildFilePath
from burninnk.write import BurninWriteV1, WriteOutput


def submit_render_job():
    try:
        output: WriteOutput | None = BurninWriteV1(
            run_execute=False, generate_thumbnail=False
        )

        burnin_client = BurninClient(nuke._burnin_client)
        thisNode = nuke.thisNode()
        write_node = thisNode.input(0)
        write_node_name = write_node.name()

        root_id_env = {}
        root_id_env["BURNIN_ROOT_ID"] = os.getenv("BURNIN_ROOT_ID")
        root_id_env["BURNIN_ROOT_NAME"] = os.getenv("BURNIN_ROOT_NAME")
        root_id_env["BURNIN_ROOT_PATH"] = os.getenv("BURNIN_ROOT_PATH")

        if output:
            print("output", output.version_node)
            print("output", output.file_path)

            version_node: Node = output.version_node
            file_path = output.file_path
            file_name = node_name_from_component_path(version_node.id.id.String)

            version_type: Version = version_node.node_type.data
            file_type: Image = version_type.file_type.data
            file_name_from_path = file_type.file_name
            start = 0
            end = 0
            if file_type.time_dependent:
                start = file_type.frame_range[0]
                end = file_type.frame_range[1]

            frame_range_arg = f"{int(start)}-{int(end)}"

            setup_file_name = file_name + "_render_setup" + ".nk"
            setup_path = file_path / setup_file_name

            file_path = str(file_path) + "\\" + file_name_from_path

            nuke.scriptSave()
            script_path = nuke.root().name()
            shutil.copy2(str(script_path), str(setup_path))
            stack = os.getenv("BU_STACK")

            job_name = file_name
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
                frame_range=[0, 0, 1],
                user_id=None,
                output_path=str(file_path),
                comment=None,
                dcc=nuke_version,
                root_id=root_id_env,
            )

            burnin_client.cmd_submit(cmd)

    except Exception as e:
        nuke.message(str(e))
        print(str(e))
